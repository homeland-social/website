from datetime import timedelta

from django.utils import timezone

from oauthlib.oauth2 import RequestValidator

from api.models import OAuthClient, OAuthAuthorizationCode, OAuthToken


class OAuthRequestValidator(RequestValidator):
    def validate_client_id(self, client_id, request, *args, **kwargs):
        # Simple validity check, does client exist? Not banned?
        return OAuthClient.objects.filter(client_id=client_id).exists()

    def validate_redirect_uri(self, client_id, redirect_uri, request, *args, **kwargs):
        # Is the client allowed to use the supplied redirect_uri? i.e. has
        # the client previously registered this EXACT redirect uri.
        return OAuthClient.objects.filter(
            client_id=client_id, redirect_uris__contains=redirect_uri).exists()

    def get_default_redirect_uri(self, client_id, request, *args, **kwargs):
        # The redirect used if none has been supplied.
        # Prefer your clients to pre register a redirect uri rather than
        # supplying one on each authorization request.
        try:
            return OAuthClient.objects.get(
                client_id=client_id).default_redirect_uri

        except OAuthClient.DoesNotExist:
            return None

    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        # Is the client allowed to access the requested scopes?
        try:
            allowed_scopes = set(
                OAuthClient.objects.get(client_id=client_id).scopes)

        except OAuthClient.DoesNotExist:
            return False

        return allowed_scopes.issuperset(set(scopes))

    def get_default_scopes(self, client_id, request, *args, **kwargs):
        # Scopes a client will authorize for if none are supplied in the
        # authorization request.
        try:
            return OAuthClient.objects.get(client_id=client_id).default_scopes

        except OAuthClient.DoesNotExist:
            return []

    def validate_response_type(self, client_id, response_type, client, request, *args, **kwargs):
        # Clients should only be allowed to use one type of response type, the
        # one associated with their one allowed grant type.
        # In this case it must be "code".
        return 'code'

    # Post-authorization

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        # Remember to associate it with request.scopes, request.redirect_uri
        # request.client and request.user (the last is passed in
        # post_authorization credentials, i.e. { 'user': request.user}.
        client = OAuthClient.objects.get(client_id=client_id)
        OAuthAuthorizationCode.objects.create(
            user=request.user,
            client=client,
            redirect_uri=request.redirect_uri,
            scopes=request.scopes,
            code=code.get('code'),
            code_state=code.get('state'),
            code_challenge=request.code_challenge,
            challenge_method=request.code_challenge_method,
            claims=code.get('claims')
        )

    # Token request

    def client_authentication_required(self, request, *args, **kwargs):
        # Check if the client provided authentication information that needs to
        # be validated, e.g. HTTP Basic auth
        return False

    def authenticate_client(self, request, *args, **kwargs):
        # Whichever authentication method suits you, HTTP Basic might work
        pass

    def authenticate_client_id(self, client_id, request, *args, **kwargs):
        # The client_id must match an existing public (non-confidential) client
        return OAuthClient.objects.filter(client_id=client_id).exists()

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        # Validate the code belongs to the client. Add associated scopes
        # and user to request.scopes and request.user.
        try:
            oauth_code = OAuthAuthorizationCode.objects.get(
                client__client_id=client_id, code=code.get('code'))

        except OAuthAuthorizationCode.DoesNotExist:
            return False

        request.user = oauth_code.user
        request.state = oauth_code.code_state
        request.scopes = oauth_code.scopes
        request.claims = oauth_code.claims
        request.code_challenge = oauth_code.challenge
        request.code_challenge_method = oauth_code.challenge_method

        return True

    def confirm_redirect_uri(self, client_id, code, redirect_uri, client, request, *args, **kwargs):
        # You did save the redirect uri with the authorization code right?
        try:
            oauth_code = OAuthAuthorizationCode.objects.get(
                client__client_id=client_id, code=code.get('code'))

        except OAuthAuthorizationCode.DoesNotExist:
            return False

        return oauth_code.redirect_uri == redirect_uri

    def validate_grant_type(self, client_id, grant_type, client, request, *args, **kwargs):
        # Clients should only be allowed to use one type of grant.
        # In this case, it must be "authorization_code" or "refresh_token"
        try:
            oauth_code = OAuthAuthorizationCode.objects.get(
                client__client_id=client_id, code=code.get('code'))

        except OAuthAuthorizationCode.DoesNotExist:
            return False

        return oauth_code.grant_type == grant_type

    def save_bearer_token(self, token, request, *args, **kwargs):
        # Remember to associate it with request.scopes, request.user and
        # request.client. The two former will be set when you validate
        # the authorization code. Don't forget to save both the
        # access_token and the refresh_token and set expiration for the
        # access_token to now + expires_in seconds.
        client = OAuthClient.objects.get(client_id=client_id)
        OAuthToken.objects.create(
            client=client,
            user=request.user,
            scopes=request.scopes,
            access_token=token.get('access_token'),
            refresh_token=token.get('refresh_token'),
            claims=request.claims,
            expires=timezone.now() + timedelta(seconds=token.get('expires_in'))
        )
        return client.default_redirect_uri

    def invalidate_authorization_code(self, client_id, code, request, *args, **kwargs):
        # Authorization codes are use once, invalidate it when a Bearer token
        # has been acquired.
        OAuthAuthorizationCode.objects.filter(
            client__client_id=client_id, code=code.get('code')).delete()

    # Protected resource request

    def validate_bearer_token(self, token, scopes, request):
        # Remember to check expiration and scope membership
        try:
            oauth_token = OAuthToken.objects.get(access_token=token)

        except OAuthToken.DoesNotExist:
            return False

        return set(oauth_token.scopes).issuperset(set(scopes))

    # Token refresh request

    def get_original_scopes(self, refresh_token, request, *args, **kwargs):
        # Obtain the token associated with the given refresh_token and
        # return its scopes, these will be passed on to the refreshed
        # access token if the client did not specify a scope during the
        # request.
        try:
            return OAuthToken.objects.get(refresh_token=refresh_token).scopes

        except OAuthToken.DoesNotExist:
            return False
