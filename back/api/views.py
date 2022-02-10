import re
import itertools
import hmac
import socket
from pprint import pprint
from urllib.parse import urlparse, urlunparse

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

from api.models import SSHKey
from api.serializers import (
    UserSerializer, OAuth2AuthzCodeSerializer, SSHKeySerializer,
)
from api.oauth import SERVER, OAuth2Scope


User = get_user_model()


class PortScanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        host = request.META['REMOTE_ADDR']
        ports = map(int, request.data['port'])
        port_status = {}

        for port in ports:
            port_status[port] = 'closed'
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.settimeout(3)
                r = s.connect_ex((host, port))
                port_status[port] = 'open' if r == 0 else 'closed'

            except socket.error as e:
                LOGGER.info(
                    'Could not connect to port %i: %s', port, e.args[0])

            finally:
                s.close()

        return Response(json.dumps(port_status), status=status.HTTP_200_OK)


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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response('', status=status.HTTP_204_NO_CONTENT)


class UserCreateView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        user = User.objects.create_user(
            request.data['email'],
            request.data['password'],
            username=request.data['username']
        )
        user.send_confirmation_email(request)
        serializer = self.serializer_class(user)
        return Response(serializer.data)


class UserWhoamiView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            email = request.query_params['email']
            ts = float(request.query_params['ts'])
            signature = request.query_params['signature']

        except ValueError as e:
            return Response({ 'ts': 'Is invalid' }, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            return Response({ e.args[0]: 'Is required' }, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, email=email)
        try:
            user.validate_confirmation(ts, signature)

        except ValueError as e:
            return Response({ 'signature': 'Is invalid' }, status=status.HTTP_400_BAD_REQUEST)

        next = request.query_params.get('next', '/#/login')
        return HttpResponseRedirect(next)


class OAuthAuthorizationView(APIView):
    permission_classes = [IsAuthenticated]

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


class SSHKeyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SSHKeySerializer
    queryset = SSHKey.objects.all()
    lookup_field = 'name'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, name=None):
        "Overridden to update or create."
        key, created = SSHKey.objects.update_or_create(
            name=name, user=request.user, defaults=request.data)
        serializer = self.serializer_class(key)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'], permission_classes=[AllowAny])
    def verify(self, request, name=None):
        try:
            key_data = request.data['key']
            key_type = request.data['type']

        except KeyError as e:
            return Response('', status.HTTP_400_BAD_REQUEST)

        key = get_object_or_404(SSHKey, name=name)
        valid = hmac.compare_digest(
            key.key, key_data) and key.type == key_type

        if not valid:
            return Response('', status.HTTP_401_UNAUTHORIZED)
        else:
            return Response('OK', status.HTTP_200_OK)
