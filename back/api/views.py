import re
import itertools
import hmac
import socket
import json
from urllib.parse import urlparse, urlunparse
from functools import cache as memoize

import dns.resolver

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
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.mixins import DestroyModelMixin
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated,
)

from api.permissions import CreateOrIsAuthenticated
from api.models import SSHKey, Hostname, OAuth2Token, Console
from api.serializers import (
    UserSerializer, OAuth2AuthzCodeSerializer, SSHKeySerializer,
    HostnameSerializer, OAuth2TokenSerializer, UserConfirmSerializer,
    ConsoleSerializer,
)
from api.oauth import SERVER, OAuth2Scope


RESOLVER = dns.resolver.Resolver(configure=False)
RESOLVER.nameservers = settings.NAME_SERVERS

User = get_user_model()


@memoize
def _load_pub():
    with open(settings.AUTHLIB_JWK_PUB, 'rb') as f:
        return json.load(f)


class UserViewSet(ModelViewSet):
    permission_classes = [CreateOrIsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'uid'

    def get_queryset(self):
        return self.queryset.filter(pk=self.request.user.id)

    def perform_create(self, serializer):
        user = serializer.save()
        user.send_confirmation_email(self.request)

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def login(self, request):
        email = request.data['email']
        password = request.data['password']
        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response('', status=status.HTTP_401_UNAUTHORIZED)
        login(request, user)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['POST'], permission_classes=[AllowAny])
    def logout(self, request):
        logout(request)
        return Response('', status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['GET'], permission_classes=[AllowAny])
    def whoami(self, request):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], permission_classes=[AllowAny])
    def confirm(self, request, uid=None):
        next = request.query_params.get('next', '/#/login')
        serializer = UserConfirmSerializer(uid, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
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


class OAuth2TokenViewSet(DestroyModelMixin, ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = OAuth2TokenSerializer
    queryset = OAuth2Token.objects.all()
    lookup_field = 'uid'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class OpenIDCMetadataView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(
            settings.AUTHLIB_OPENIDC_METADATA, status=status.HTTP_200_OK)


class OAuthJWKSView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({ 'keys': [_load_pub()]}, status=status.HTTP_200_OK)


class SSHKeyViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SSHKeySerializer
    queryset = SSHKey.objects.all()
    lookup_field = 'uid'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-created')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def update(self, request, name=None):
        "Overridden to update or create."
        key, created = SSHKey.objects.update_or_create(
            name=name, user=request.user, defaults=request.data)
        serializer = self.serializer_class(key)
        return Response(serializer.data)


class HostnameViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HostnameSerializer
    queryset = Hostname.objects.all()
    lookup_field = 'uid'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'])
    def shared(self, request):
        return Response(settings.SHARED_DOMAINS, status=status.HTTP_200_OK)

    @action(detail=False, url_path=r'(?P<name>[^/]+)/dig', methods=['POST'])
    def dig(self, request, name=None):
        hostname = get_object_or_404(Hostname, name=name)
        result = {}
        try:
            a = RESOLVER.query(hostname.name, 'A')
            result[hostname.name] = [ip.to_text() for ip in a]

        except dns.resolver.NXDOMAIN:
            result[hostname.name] = None

        return Response(result, status.HTTP_200_OK)

    @action(detail=False, methods=['POST'])
    def port_scan(self, request):
        host = request.META['REMOTE_ADDR']
        ports = map(int, request.data.get('ports', [80, 443]))
        response = {
            'host': host,
        }

        for port in ports:
            response[port] = 'closed'
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.settimeout(3)
                r = s.connect_ex((host, port))
                response[port] = 'open' if r == 0 else 'closed'

            except socket.error as e:
                LOGGER.info(
                    'Could not connect to port %i: %s', port, e.args[0])

            finally:
                s.close()

        return Response(response, status=status.HTTP_200_OK)


class ConsoleViewSet(ModelViewSet):
    serializer_class = ConsoleSerializer
    permission_classes = [IsAuthenticated]
    queryset = Console.objects.all()
    lookup_field = 'uuid'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'], permission_classes=[AllowAny])
    def verify_key(self, request, uuid=None):
        try:
            key_data = request.data['key']
            key_type = request.data['type']

        except KeyError as e:
            return Response(
                {e.args[0]: 'Is required'}, status.HTTP_400_BAD_REQUEST,
                content_type='application/json')

        valid, console = False, get_object_or_404(Console, uuid=uuid)
        for sshkey in console.user.sshkeys.all():
            if hmac.compare_digest(sshkey.key, key_data) and \
               sshkey.type == key_type:
                valid = True
                break

        if not valid:
            return Response({'key': 'Invalid'}, status.HTTP_400_BAD_REQUEST,
                            content_type='application/json')

        else:
            serializer = SSHKeySerializer(sshkey)
            return Response(serializer.data, status.HTTP_200_OK,
                            content_type='application/json')

    @action(detail=True, methods=['POST'], permission_classes=[AllowAny])
    def verify_host(self, request, uuid=None):
        try:
            domain = request.data['domain']

        except KeyError as e:
            return Response(
                {e.args[0]: 'Is required'}, status.HTTP_400_BAD_REQUEST,
                content_type='application/json')

        console = get_object_or_404(Console, uuid=uuid)
        try:
            host = console.user.hosts.get(name=domain)

        except Hostname.DoesNotExist:
            return Response({'domain': 'Invalid'}, status.HTTP_400_BAD_REQUEST,
                            content_type='application/json')

        else:
            serializer = HostnameSerializer(host)
            return Response(serializer.data, status=status.HTTP_200_OK)
