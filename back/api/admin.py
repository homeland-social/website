from django.contrib import admin
from django.contrib.auth.forms import (
    UserCreationForm as _UserCreationForm, UserChangeForm as _UserChangeForm
)
from django.contrib.auth.admin import UserAdmin as _UserAdmin
from django.utils.translation import gettext_lazy as _

from api.models import User, SSHKey, Hostname, OAuth2Client, Console


class UserCreationForm(_UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class UserChangeForm(_UserChangeForm):
    class Meta:
        model = User
        fields = ('email',)


@admin.register(User)
class UserAdmin(_UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "is_confirmed")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

@admin.register(SSHKey)
class SSHKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "user", "console")


@admin.register(Hostname)
class HostnameAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "console")


@admin.register(OAuth2Client)
class OAuth2ClientAdmin(admin.ModelAdmin):
    list_display = ("user", "client_id", "client_name", "website_uri")


@admin.register(Console)
class ConsoleAdmin(admin.ModelAdmin):
    list_display = ("uuid", "user")
