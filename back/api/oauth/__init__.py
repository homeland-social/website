from authlib.integrations.django_oauth2 import (
    AuthorizationServer, BearerTokenValidator,
)
from authlib.oauth2.rfc6749 import grants
from authlib.common.security import generate_token

from rest_framework import authentication
from rest_framework import exceptions

from django.contrib.auth import get_user_model

from api.models import OAuth2Client, OAuth2Token, OAuth2Code


SERVER = AuthorizationServer(OAuth2Client, OAuth2Token)
User = get_user_model()


class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def save_authorization_code(self, code, request):
        return OAuth2Code.objects.create(
            code=code,
            client_id=request.client.client_id,
            redirect_uri=request.redirect_uri,
            response_type=request.response_type,
            scope=request.client.scope,
            user=request.user,
        )

    def query_authorization_code(self, code, client):
        try:
            item = OAuth2Code.objects.get(code=code, client_id=client.client_id)
        except OAuth2Code.DoesNotExist:
            return None

        if not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        authorization_code.delete()

    def authenticate_user(self, authorization_code):
        return authorization_code.user


class RefreshTokenGrant(grants.RefreshTokenGrant):
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
        return (token.user, None)

    def authenticate(self, request):
        return self._authenticate(request.META)


SERVER.register_grant(AuthorizationCodeGrant)
SERVER.register_grant(RefreshTokenGrant)
