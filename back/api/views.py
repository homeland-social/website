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
    SSHKey,
)
from api.serializers import (
    UserSerializer, OAuth2AuthzCodeSerializer, CreateUserSerializer,
    SSHKeySerializer,
)
from api.oauth import SERVER, OAuth2Scope


User = get_user_model()


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

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
