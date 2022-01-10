from django.urls import path

from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from api.views import (
    ServiceViewSet, ServiceVersionViewSet, UserCreateView, UserConfirmView,
)


router = routers.SimpleRouter()
router.register(r'services/', ServiceViewSet, basename='service')
router.register(r'services/<uuid>/', ServiceVersionViewSet, basename='serviceversion')

urlpatterns = [
    path(
        r'token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair_view'
    ),
    path(
        r'token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh_view'
    ),
    path(
        r'token/verfiy/',
        TokenVerifyView.as_view(),
        name='token_verify_view'
    ),

    path(r'users/create/', UserCreateView.as_view(), name='api_users_create'),
    path(r'users/confirm/', UserConfirmView.as_view(), name='api_users_confirm'),
] + router.urls
