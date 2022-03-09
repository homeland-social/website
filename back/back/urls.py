from django.urls import path, include
from django.contrib import admin


urlpatterns = [
    path(r'api/', include('api.urls')),
    path('admin/', admin.site.urls)
]
