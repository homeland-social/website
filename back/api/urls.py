from django.urls import path

from rest_framework import routers

from api.views import (
    OAuthAuthorizationView, OAuthTokenView, SSHKeyViewSet, HostnameViewSet,
    OAuth2TokenViewSet, UserViewSet, OAuthJWKSView, OpenIDCMetadataView,
    ConsoleViewSet,
)


router = routers.SimpleRouter()
router.register(r'sshkeys', SSHKeyViewSet, basename='sshkey')
router.register(r'hosts', HostnameViewSet, basename='host')
router.register(r'tokens', OAuth2TokenViewSet, basename='token')
router.register(r'users', UserViewSet, basename='user')
router.register(r'consoles', ConsoleViewSet, basename='console')

urlpatterns = [
    path(
        r'oauth2/authorize/',
        OAuthAuthorizationView.as_view(),
        name='oauth_authorize_view'
    ),
    path(
        r'oauth2/token/',
        OAuthTokenView.as_view(),
        name='oauth_token_view'
    ),
    path(
        r'oauth2/jwks/',
        OAuthJWKSView.as_view(),
        name='oauth_jwks_view'
    ),
    path(
        r'oauth2/metadata/',
        OpenIDCMetadataView.as_view(),
        name='oauth_openidc_metadata_view'
    ),
] + router.urls
