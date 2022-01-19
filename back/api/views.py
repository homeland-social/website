import re
import itertools
from pprint import pprint
from urllib.parse import urlparse, urlunparse

import pycosat

from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth import get_user_model, login, logout, authenticate
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from cache_memoize import cache_memoize
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated,
)

from api.models import (
    Service, ServiceVersion, ServiceConflict, ServiceRequire,
)
from api.serializers import (
    ServiceSerializer, ServiceVersionSerializer, UserSerializer,
    OAuth2AuthzCodeSerializer, CreateUserSerializer,
)
from api.oauth import SERVER


User = get_user_model()


# Repository data.
PACKAGES = {
    'A': {
        '1.0.0': {
            'conflicts': [
                ('B', '9.2'),
            ],
        },
        '1.0.1': {
            'conflicts': [
                ('B', '9.2'),
            ],
            'requires': [
                ('C', '2.0'),
            ],
        },
    },
    'B': {
        '9.2': {},
    },
    'C': {
        '2.0': {},
        '1.0': {
            'conflicts': [
                ('B', '9.2'),
            ],
        },
    },
}

# Currently installed packages.
INSTALLED_PACKAGES = [
    ('C', '1.0'),
]

# User selected packages.
SELECTED_PACKAGES = [
    ('A', None)
]


@cache_memoize(60 * 60)
def get_service_meta():
    pkgs = {}

    # Assign each package an id.
    id = 0
    for n, i in PACKAGES.items():
        for v, i in i.items():
            id += 1
            pkgs[id] = (n, v)

    # Reverse lookups...
    rpkg = {v: n for n, v in pkgs.items()}

    # This preamble can be cached.
    states = []
    for id, (n, v) in pkgs.items():
        info = PACKAGES[n][v]
        vers = [k for k in PACKAGES[n].keys() if k != v]
        for o in vers:
            states.append([-id, -rpkg[(n, o)]])
        for c in info.get('conflicts', ()):
            states.append([-id, -rpkg[c]])
        for r in info.get('requires', ()):
            states.append([-id, rpkg[r]])

    return pkgs, rpkg, states


@receiver([post_save, post_delete])
def clear_service_meta(sender, **kwargs):
    if sender.__class__ in (Service, ServiceVersion, ServiceConflict,
                            ServiceRequire):
        get_service_meta.invalidate()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(request.user, 'is_admin', False)


def suggest():
    # NOTE: This algorithm does not take into account the removal of packages
    # it assumes everything installed needs to remain installed.
    def cnf():
        # NOTE: These are user-specific.
        for n, v in INSTALLED_PACKAGES:
            # TODO: Only _NEWER_ versions should be considered...
            yield [rpkg[(n, v)] for v in PACKAGES[n].keys()]

        for n, v in SELECTED_PACKAGES:
            # If the user does not specify a version, we can OR all the verion
            # ids together.
            if v is None:
                # NOTE: in this case, we end up selecting unecessary packages.
                # I am sure this can be corrected, but I am not sure how.
                # Once I have unit testing set up for this experiment, I can
                # figure it out quickly.
                # NOTE: if we solve this, the cost calculation below can be
                # eliminated.
                yield [rpkg[(n,v)] for v in PACKAGES[n].keys()]
            else:
                yield [rpkg[(n, v)]]

    def _print_exp(exp, pre=''):
        def _format(id):
            sign = '+' if id > 0 else '-'
            n, v = pkgs[abs(id)]
            return f'{sign}{n}-{v}'

        print(pre + ', '.join([_format(id) for id in exp]))

    def _debug(cnf):
        for exp in cnf:
            _print_exp(exp, pre='Repo: ')
            yield exp

    def calc_cost(sol):
        "Calculate cost of a solution."
        # TODO: this should filter out all the packages that are NOT changing.
        cost, filtered = 1000, []
        for id in sol:
            n, v = pkgs[abs(id)]
            if id < 0:
                # Only care about additional packages.
                continue
            if n not in [o[0] for o in SELECTED_PACKAGES + INSTALLED_PACKAGES]:
                # Add 100 for each extraneous package.
                cost += 100
            else:
                # Subtract the abs value of the version (prefer higher versions)
                cost -= int(''.join([a for a in v if a.isdigit()]))
        return cost, sol

    pkgs, rpkg, states = get_service_meta()

    data = itertools.chain(states, cnf())
    if settings.DEBUG:
        data = _debug(data)

    solutions = []
    for sol in pycosat.itersolve(data):
        cost, sol = calc_cost(sol)
        print_exp(sol, pre=f'Solu [{cost}]: ')
        solutions.append((cost, sol))

    if solutions:
        print_exp(sorted(solutions, key=lambda x: x[0])[0][1], pre='Final: ')


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'uuid'
    lookup_value_regex = '[0-9a-f\-]{36}'

    def list(self, request):
        services = self.get_queryset()
        serializer = self.serializer_class(services, many=True)
        return Response(serializer.data)

    def retrieve(self, request, uuid=None):
        service = get_object_or_404(Service, uuid=uuid)
        serializer = self.serializer_class(service)
        return Response(serializer.data)

    def create(self, request):
        service = Service.objects.create(**request.data)
        serializer = self.serializer_class(service)
        return Response(serializer.data)

    def delete(self, request):
        service = get_object_or_404(Service, uuid=uuid)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def suggest(self, request):
        installed_packages = self.data.get('installed')
        selected_packages = self.data.get('selected')
        pkgids, rpkgids, packages = get_service_meta()


class ServiceVersionViewSet(ModelViewSet):
    queryset = ServiceVersion.objects.all()
    serializer_class = ServiceVersionSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'version'
    lookup_value_regex = '[0-9\.]+'

    def list(self, request, uuid=None):
        service = get_object_or_404(Service, uuid=uuid)
        serializer = self.serializer_class(service.versions.all(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, uuid=None, version=None):
        service = get_object_or_404(Service, uuid=uuid)
        version = get_object_or_404(ServiceVersion, service=service, version=version)
        serializer = self.serializer_class(version)
        return Response(serializer.data)

    def create(self, request, uuid=None):
        service = get_object_or_404(Service, uuid=uuid)
        version = ServiceVersion.objects.create(service=service, **request.data)
        serializer = self.serializer_class(version)
        return Response(serializer.data)

    def delete(self, pk, request):
        service = get_object_or_404(Service, uuid=uuid)
        version = get_object_or_404(ServiceVersion, service=service, version=version)
        version.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserLoginView(APIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data['email']
        password = request.data['password']
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response('', status=status.HTTP_401_UNAUTHORIZED)
        login(request, user)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserLogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response('', status=status.HTTP_204_NO_CONTENT)


class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        user = User.objects.create_user(
            request.data['email'],
            request.data['password'],
            username=request.data['username']
        )
        user.send_confirmation_email(request)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class UserWhoamiView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data['email']
            ts = float(request.data['ts'])
            signature = request.data['signature']

        except ValueError as e:
            return Response({ 'ts': 'Is invalid' }, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({ e.args[0]: 'Is required' }, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, email=email)
        try:
            user.validate_confirmation(ts, signature)

        except ValueError as e:
            return Response({ 'signature': 'Is invalid' }, status=status.HTTP_400_BAD_REQUEST)

        next = request.query.get('next', '/#/login')
        return HttpResponseRedirect(next)


class OAuthAuthorizationView(APIView):
    def get(self, request):
        grant = SERVER.validate_consent_request(request)
        serializer = OAuth2AuthzCodeSerializer(grant)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        is_confirmed = request.data.get('confirm') == 'true'
        user = request.user if is_confirmed else None
        # NOTE: returns a redirect, no serialization necessary.
        return SERVER.create_authorization_response(request, grant_user=user)


class OAuthTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        return SERVER.create_token_response(request)
