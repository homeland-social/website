import logging

from authlib.integrations.django_oauth2 import (
    AuthorizationServer, BearerTokenValidator,
)
from authlib.oauth2.rfc6749 import grants
from authlib.common.security import generate_token

from rest_framework import authentication, exceptions, permissions

from django.contrib.auth import get_user_model

from api.models import OAuth2Client, OAuth2Token, OAuth2Code


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

SERVER = AuthorizationServer(OAuth2Client, OAuth2Token)
User = get_user_model()


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def save_authorization_code(self, code, request):
        return OAuth2Code.objects.create(
            code=code,
            client=request.client,
            redirect_uri=request.redirect_uri,
            response_type=request.response_type,
            scope=request.client.scope,
            user=request.user,
        )

    def query_authorization_code(self, code, client):
        try:
            item = OAuth2Code.objects.get(code=code, client__client_id=client.client_id)

        except OAuth2Code.DoesNotExist:
            return None

        if not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        authorization_code.delete()

    def authenticate_user(self, authorization_code):
        return authorization_code.user


class RefreshTokenGrant(grants.RefreshTokenGrant):
    INCLUDE_NEW_REFRESH_TOKEN = True

    def authenticate_refresh_token(self, refresh_token):
        try:
            item = OAuth2Token.objects.get(refresh_token=refresh_token)
            if item.is_refresh_token_active():
                return item
        except OAuth2Token.DoesNotExist:
            return None

    def authenticate_user(self, credential):
        return credential.user

    def revoke_old_credential(self, credential):
        credential.revoked = True
        credential.save()


class OAuth2Authentication(authentication.BaseAuthentication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._validator = BearerTokenValidator(OAuth2Token)

    def _authenticate(self, environ):
        token_string = environ.get('HTTP_AUTHORIZATION', None)
        if not token_string or not token_string.startswith('Bearer '):
            return None
        token = self._validator.authenticate_token(token_string[7:])
        if token is None:
            return None
        return token

    def authenticate(self, request):
        token = self._authenticate(request.META)
        if token is None:
            return None
        request.auth = token
        return (token.user, None)


class OAuth2Scope(permissions.BasePermission):
    def has_permission(self, request, view):
        token = getattr(request, 'auth', None)
        if token is None:
            # Did not authenticate with oauth.
            return True

        scopes = token.scope
        required_scopes = self.get_scopes(request, view)

        if isinstance(required_scopes, dict):
            required_scopes = required_scopes.get(request.method, [])

        assert isinstance(required_scopes, list), \
            'required_scopes must be dict or list'

        return set(scopes).issuperset(set(required_scopes))

    def get_scopes(self, request, view):
        try:
            return getattr(view, 'required_scopes')

        except AttributeError:
            LOGGER.warning(
                'Could not determine acceptable scopes for view %s'
                % view.__class__.__name__)
            return []


SERVER.register_grant(AuthorizationCodeGrant)
SERVER.register_grant(RefreshTokenGrant)
