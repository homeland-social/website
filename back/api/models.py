import time
import hmac
import binascii
from datetime import timedelta
from uuid import uuid4

from pkg_resources import parse_version
from pkg_resources.extern.packaging.version import Version
from authlib.oauth2.rfc6749 import (
    ClientMixin, TokenMixin, AuthorizationCodeMixin,
)

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.http import urlencode
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.postgres.fields import ArrayField

from mail_templated import send_mail


GRANT_TYPES = [
    ('authorization_code', 'authorization_code'),
]
TOKEN_AUTH_METHODS = [
    ('client_secret_post', 'client_secret_post'),
    ('client_secret_basic', 'client_secret_basic'),
]


class VersionField(models.CharField):
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return parse_version(value)

    def to_python(self, value):
        if isinstance(value, Version):
            return value

        if value is None:
            return value

        return parse_version(value)

    def get_prep_value(self, value):
        return str(value)


class UserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        kwargs.setdefault('is_active', False)
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_confirmed', True)

        if kwargs['is_staff'] is not True:
            raise ValueError('is_staff must be True')
        if kwargs['is_superuser'] is not True:
            raise ValueError('is_superuser must be True')

        return self.create_user(email, password, **kwargs)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    username = models.CharField(max_length=32)
    email = models.EmailField('email address', unique=True)
    is_confirmed = models.BooleanField(default=False)

    objects = UserManager()

    def generate_confirmation(self, ts=None):
        email = self.email
        if ts is None:
            ts = time.time()
        key = settings.SECRET_KEY.encode('utf8')
        message = b'%i--%s' % (ts, email.encode('utf8'))
        signature = binascii.hexlify(hmac.digest(key, message, 'sha256'))
        return {
            'email': email,
            'ts': ts,
            'signature': signature,
        }

    def send_confirmation_email(self, request):
        params = self.generate_confirmation()
        url = request.build_absolute_url(reverse('api_users_confirm'))
        url += '?' + urlencode(params)
        send_mail(
            'email/user_confirmation.eml',
            { 'url': url },
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
        )

    def validate_confirmation(self, ts, signature):
        params = self.generate_confirmation(ts)
        sig1 = binascii.unhexlify(params['signature'])
        sig2 = binascii.unhexlify(signature)
        if time.time() - ts > settings.EMAIL_CONFIRM_DAYS * 86400:
            raise ValueError('Signature expired')
        if not hmac.compare_digest(sig1, sig2):
            raise ValueError('Invalid signature')
        User.objects.filter(pk=self.pk).update(
            is_active=True, is_confirmed=True)
        return True


class Service(models.Model):
    uuid = models.CharField(max_length=36, default=uuid4, unique=True)
    name = models.CharField(unique=True, max_length=32)
    description = models.TextField()
    group = models.CharField(max_length=32)
    logo = models.URLField(null=True)
    created = models.DateTimeField(null=False, auto_now_add=True)


class ServiceVersion(models.Model):
    service = models.ForeignKey(
        Service, related_name='versions', on_delete=models.CASCADE)
    version = VersionField(max_length=16)
    image_name = models.CharField(max_length=64)
    image_tag = models.CharField(max_length=16)
    created = models.DateTimeField(null=False, auto_now_add=True)


class ServiceRequire(models.Model):
    class Meta:
        unique_together = ('requiring', 'required')

    requiring = models.ForeignKey(
        ServiceVersion, related_name='requires', on_delete=models.CASCADE)
    required = models.ForeignKey(
        ServiceVersion, related_name='required_by', on_delete=models.CASCADE)


class ServiceConflict(models.Model):
    class Meta:
        unique_together = ('conflicting', 'conflicted')

    conflicting = models.ForeignKey(
        ServiceVersion, related_name='conflicts', on_delete=models.CASCADE)
    conflicted = models.ForeignKey(
        ServiceVersion, related_name='conflicts_with',
        on_delete=models.CASCADE)


class SSHKey(models.Model):
    user = models.ForeignKey(User, db_index=True,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True)
    key = models.TextField(max_length=2000)
    keytype = models.CharField(
        max_length=32, blank=True, help_text="Type of key, e.g. 'ssh-rsa'")
    fingerprint = models.CharField(max_length=128, blank=True, db_index=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(auto_now=True)


# https://docs.authlib.org/en/latest/django/2/authorization-server.html
class OAuth2Client(models.Model, ClientMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=36, default=uuid4, unique=True)
    client_secret = models.CharField(max_length=36, default=uuid4, null=False)
    client_name = models.CharField(max_length=120)
    website_uri = models.URLField(max_length=256, null=True)
    description = models.TextField(null=True)
    redirect_uris = ArrayField(models.CharField(max_length=256))
    default_redirect_uri = models.CharField(max_length=256, null=True)
    scope = ArrayField(models.CharField(max_length=24), null=True)
    response_type = models.TextField(null=True)
    grant_type = models.TextField(
        choices=GRANT_TYPES, null=False, default='authorization_code')
    token_endpoint_auth_method = models.CharField(
        choices=TOKEN_AUTH_METHODS, max_length=120, null=False, default='client_secret_post')

    def get_client_id(self):
        return self.client_id

    def get_default_redirect_uri(self):
        return self.default_redirect_uri

    def get_allowed_scope(self, scope):
        if not scope:
            return []
        return [s for s in scope if s in self.scope]

    def check_redirect_uri(self, redirect_uri):
        if redirect_uri == self.default_redirect_uri:
            return True
        return redirect_uri in self.redirect_uris

    def has_client_secret(self):
        return bool(self.client_secret)

    def check_client_secret(self, client_secret):
        return self.client_secret == client_secret

    def check_token_endpoint_auth_method(self, method):
        return self.token_endpoint_auth_method == method

    def check_response_type(self, response_type):
        allowed = self.response_type.split()
        return response_type in allowed

    def check_grant_type(self, grant_type):
        allowed = self.grant_type.split()
        return grant_type in allowed


class OAuth2Token(models.Model, TokenMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=36, db_index=True)
    token_type = models.CharField(max_length=40)
    access_token = models.CharField(max_length=255, unique=True, null=False)
    refresh_token = models.CharField(max_length=255, db_index=True, null=False)
    scope = ArrayField(models.CharField(max_length=24), null=True)
    revoked = models.BooleanField(default=False)
    issued_at = models.DateTimeField(null=False, default=timezone.now)
    expires_in = models.IntegerField(null=False, default=0)

    def get_client_id(self):
        return self.client_id

    def get_scope(self):
        return self.scope

    def get_expires_in(self):
        return self.expires_in

    def get_expires_at(self):
        return self.issued_at + timedelta(seconds=self.expires_in)


class OAuth2Code(models.Model, AuthorizationCodeMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=36, db_index=True)
    code = models.CharField(max_length=120, unique=True, null=False)
    redirect_uri = models.TextField(null=True)
    response_type = models.TextField(null=True)
    scope = ArrayField(models.CharField(max_length=24), null=True)
    auth_time = models.DateTimeField(null=False, default=timezone.now)

    def is_expired(self):
        return self.auth_time + timedelta(seconds=300) < timezone.now()

    def get_redirect_uri(self):
        return self.redirect_uri

    def get_scope(self):
        return self.scope

    def get_auth_time(self):
        return self.auth_time
