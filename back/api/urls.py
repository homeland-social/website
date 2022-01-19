from django.urls import path

from rest_framework import routers

from api.views import (
    ServiceViewSet, ServiceVersionViewSet, UserLoginView, UserLogoutView,
    UserCreateView, UserWhoamiView, UserConfirmView, OAuthAuthorizationView,
    OAuthTokenView,
)


router = routers.SimpleRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'services/(?P<uuid>[0-9a-f\-]{36})/versions', ServiceVersionViewSet, basename='serviceversion')

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

    path(r'users/login/', UserLoginView.as_view(), name='api_users_login'),
    path(r'users/logout/', UserLogoutView.as_view(), name='api_users_logout'),
    path(r'users/create/', UserCreateView.as_view(), name='api_users_create'),
    path(r'users/whoami/', UserWhoamiView.as_view(), name='api_users_whoami'),
    path(r'users/confirm/', UserConfirmView.as_view(), name='api_users_confirm'),
] + router.urls
