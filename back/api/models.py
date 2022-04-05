import time
import hmac
import binascii
import logging
from datetime import timedelta
from uuid import uuid4

from hashids import Hashids

from authlib.oauth2.rfc6749 import (
    ClientMixin, TokenMixin, AuthorizationCodeMixin,
)

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.http import urlencode
from django.utils.functional import cached_property
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.postgres.fields import ArrayField

from mail_templated import send_mail


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

GRANT_TYPES = [
    ('authorization_code', 'authorization_code'),
]
TOKEN_AUTH_METHODS = [
    ('client_secret_post', 'client_secret_post'),
    ('client_secret_basic', 'client_secret_basic'),
]

HASHIDS_LENGTH = 12


def grant_types_default():
    return ['authorization_code', 'refresh_token']


class HashidsQuerySet(models.QuerySet):
    def get(self, *args, **kwargs):
        uid = kwargs.pop('uid', None)
        if uid:
            try:
                kwargs['id'] = self.model.hashids().decode(uid)[0]

            except IndexError:
                LOGGER.exception('Error decoding hashid')
                kwargs['id'] = None
        return super().get(*args, **kwargs)

    def filter(self, *args, **kwargs):
        uid = kwargs.pop('uid', None)
        if uid:
            try:
                kwargs['id'] = self.model.hashids().decode(uid)[0]

            except IndexError:
                LOGGER.exception('Error decoding hashid')
                kwargs['id'] = None
        return super().filter(*args, **kwargs)


class HashidsManagerMixin:
    def get_queryset(self):
        return HashidsQuerySet(
            model=self.model, using=self._db, hints=self._hints)


class HashidsManager(HashidsManagerMixin, models.Manager):
    pass


class HashidsModelMixin:
    @classmethod
    def hashids(cls):
        hashids = getattr(cls, '_hashids', None)
        if not hashids:
            hashids = Hashids(
                min_length=HASHIDS_LENGTH, salt=f'{cls.__name__}:{settings.SECRET_KEY}')
            setattr(cls, '_hashids', hashids)
        return hashids

    @property
    def uid(self):
        return self.hashids().encode(self.id)


class UserManager(HashidsManagerMixin, BaseUserManager):
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


class User(HashidsModelMixin, AbstractUser):
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
        url = request.build_absolute_uri(
            reverse('user-confirm', kwargs={'uid': self.uid}))
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
        return True


class Console(models.Model):
    uuid = models.UUIDField(null=False, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(null=False, default=uuid4)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(auto_now=True)
    used = models.DateTimeField(null=True)

    def __str__(self):
        return f'Console: uuid={self.uuid}'


class SSHKey(HashidsModelMixin, models.Model):
    user = models.ForeignKey(User, db_index=True, related_name='sshkeys',
                             on_delete=models.CASCADE)
    console = models.ForeignKey(
        Console, related_name='sshkeys', on_delete=models.CASCADE)
    name = models.UUIDField(unique=True, default=uuid4)
    key = models.TextField(max_length=2000)
    type = models.CharField(max_length=20)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(auto_now=True)

    objects = HashidsManager()


class Hostname(HashidsModelMixin, models.Model):
    user = models.ForeignKey(User, db_index=True, related_name='hosts',
                             on_delete=models.CASCADE)
    console = models.ForeignKey(
        Console, related_name='hosts', on_delete=models.CASCADE)
    name = models.CharField(max_length=128, unique=True)
    addresses = ArrayField(
        models.GenericIPAddressField(), null=True
    )
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(auto_now=True)

    objects = HashidsManager()

    @cached_property
    def internal(self):
        for domain in settings.SHARED_DOMAINS:
            if self.name.endswith(f'.{domain}'):
                return True
        return False


# https://docs.authlib.org/en/latest/django/2/authorization-server.html
class OAuth2Client(HashidsModelMixin, models.Model, ClientMixin):
    class Meta:
        verbose_name = "OAuth2 Client"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client_id = models.UUIDField(unique=True)
    client_secret = models.UUIDField(null=False)
    client_name = models.CharField(max_length=120)
    website_uri = models.URLField(max_length=256, null=True)
    description = models.TextField(null=True)
    redirect_uris = ArrayField(models.CharField(max_length=256))
    default_redirect_uri = models.CharField(max_length=256, null=True)
    scope = ArrayField(models.CharField(max_length=24), null=True)
    response_types = ArrayField(models.CharField(max_length=32), null=True)
    grant_types = ArrayField(
        models.CharField(max_length=32), null=False,
        default=grant_types_default)
    token_endpoint_auth_method = models.CharField(
        choices=TOKEN_AUTH_METHODS, max_length=120, null=False,
        default='client_secret_post')

    objects = HashidsManager()

    def get_client_id(self):
        return str(self.client_id)

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
        return str(self.client_secret) == client_secret

    def check_endpoint_auth_method(self, method, endpoint):
        return endpoint != 'token' or self.token_endpoint_auth_method == method

    def check_response_type(self, response_type):
        return response_type in self.response_types

    def check_grant_type(self, grant_type):
        return grant_type in self.grant_types
        return allowed


class OAuth2Token(HashidsModelMixin, models.Model, TokenMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(
        OAuth2Client, to_field="client_id", db_column="client", on_delete=models.CASCADE)
    token_type = models.CharField(max_length=40)
    access_token = models.CharField(max_length=255, unique=True, null=False)
    refresh_token = models.CharField(max_length=255, db_index=True, null=False)
    scope = ArrayField(models.CharField(max_length=24), null=True)
    revoked = models.BooleanField(default=False)
    issued_at = models.DateTimeField(null=False, default=timezone.now)
    expires_in = models.IntegerField(null=False, default=0)

    objects = HashidsManager()

    def get_client_id(self):
        return self.client.client_id

    def get_scope(self):
        return self.scope

    def get_expires_in(self):
        return self.expires_in

    def get_expires_at(self):
        return self.issued_at + timedelta(seconds=self.expires_in)


class OAuth2Code(HashidsModelMixin, models.Model, AuthorizationCodeMixin):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    client = models.ForeignKey(
        OAuth2Client, to_field="client_id", db_column="client", on_delete=models.CASCADE)
    code = models.CharField(max_length=120, unique=True, null=False)
    redirect_uri = models.TextField(null=True)
    response_type = models.TextField(null=True)
    scope = ArrayField(models.CharField(max_length=24), null=True)
    auth_time = models.DateTimeField(null=False, default=timezone.now)
    nonce = models.CharField(max_length=120, null=True)

    objects = HashidsManager()

    def is_expired(self):
        return self.auth_time + timedelta(seconds=300) < timezone.now()

    def get_redirect_uri(self):
        return self.redirect_uri

    def get_scope(self):
        return self.scope

    def get_auth_time(self):
        return self.auth_time.timestamp()

    def get_nonce(self):
        return self.nonce
