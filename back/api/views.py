import re
from pprint import pprint

import pycosat

from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth import get_user_model

from cache_memoize import cache_memoize
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from api.models import (
    Service, ServiceVersion, ServiceConflict, ServiceRequire,
)
from api.serializers import (
    ServiceSerializer, ServiceVersionSerializer, UserSerializer,
)


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
    pass


@receiver([post_save, post_delete])
def clear_service_meta(sender, **kwargs):
    if sender.__class__ in (Service, ServiceVersion, ServiceConflict,
                            ServiceRequire):
        get_service_meta.invalidate()


def suggest():
    # NOTE: This algorithm does not take into account the removal of packages
    # it assumes everything install needs to remain installed.
    pkgs = {}

    # Assign each package an id.
    id = 0
    for n, i in PACKAGES.items():
        for v, i in i.items():
            id += 1
            pkgs[id] = (n, v)

    # Reverse lookups...
    rpkg = {v: n for n, v in pkgs.items()}

    def cnf():
        # TODO: This first part can be cached, along with pkgs and rpkg.
        for id, (n, v) in pkgs.items():
            info = PACKAGES[n][v]
            vers = [k for k in PACKAGES[n].keys() if k != v]
            for o in vers:
                yield [-id, -rpkg[(n, o)]]
            for c in info.get('conflicts', ()):
                yield [-id, -rpkg[c]]
            for r in info.get('requires', ()):
                yield [-id, rpkg[r]]

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

    def print_exp(exp, pre=''):
        def _format(id):
            sign = '+' if id > 0 else '-'
            n, v = pkgs[abs(id)]
            return f'{sign}{n}-{v}'

        print(pre + ', '.join([_format(id) for id in exp]))

    def debug(cnf):
        for exp in cnf:
            print_exp(exp, pre='Repo: ')
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

    data = cnf()
    if settings.DEBUG:
        data = debug(data)

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
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'uuid'
    lookup_value_regex = '[0-9a-f]{32}'

    def list(self, request):
        pass

    def retrieve(self, request):
        pass

    def create(self, request):
        pass

    def delete(self, request):
        pass

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def suggest(self, request):
        installed_packages = self.data.get('installed')
        selected_packages = self.data.get('selected')
        pkgids, rpkgids, packages = get_service_meta()


class ServiceVersionViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceVersionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'version'
    lookup_value_regex = '[0-9\.]'

    def list(self, pk, request):
        pass

    def retrieve(self, pk, request):
        pass

    def create(self, pk, request):
        pass

    def delete(self, pk, request):
        pass


class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserConfirmView(APIView):
    pass
