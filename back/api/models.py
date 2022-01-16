import time
import hmac
import binascii

from pkg_resources import parse_version

from django.conf import settings
from django.db import models
from django.utils.http import urlencode
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.contrib.postgres.fields import ArrayField

from mail_templated import send_mail


class VersionField(models.CharField):
    def from_db_value(self, value, expression, connection):
        return str(value)

    def to_python(self, value):
        if value is None:
            return value

        return parse_version(value)


class UserManager(BaseUserManager):
    def create_user(self, email, password, **kwargs):
        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.set_password(password)
        user.send_confirmation_email()
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

    username = None
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

    def send_confirmation_email(self):
        params = self.generate_confirmation()
        url = settings.EMAIL_CONFIRM_URL
        url = f'{url}?{urlencode(params)}'
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


class SSHKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    pub = models.TextField()


class AccessToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    token = models.CharField(max_length=32)


class Service(models.Model):
    uuid = models.UUIDField()
    created = models.DateTimeField()
    name = models.CharField(unique=True, max_length=32)
    group = models.CharField(max_length=32)
    logo = models.URLField()
    description = models.TextField()


class ServiceVersion(models.Model):
    service = models.ForeignKey(
        Service, related_name='versions', on_delete=models.CASCADE)
    created = models.DateTimeField()
    version = VersionField(max_length=16)
    image_name = models.CharField(max_length=64)
    image_tag = models.CharField(max_length=16)


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
    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)


class OAuthClient(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    client_id = models.CharField(max_length=100, unique=True)
    grant_type = models.CharField(
        max_length=18,
        default='authorization_code',
        choices=[('authorization_code', 'Authorization code')])
    response_type = models.CharField(
        max_length=4, choices=[('code', 'Authorization code')])
    scopes = ArrayField(
        models.CharField(max_length=16, blank=False))
    default_scopes = ArrayField(
        models.CharField(max_length=16, blank=False))
    redirect_uris = ArrayField(
        models.URLField(max_length=128, blank=False))
    default_redirect_uri = models.URLField(max_length=128, null=True)


class OAuthToken(models.Model):
    client = models.ForeignKey(
        OAuthClient, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    scopes = ArrayField(
        models.CharField(max_length=16, blank=False))
    access_token = models.CharField(max_length=100, unique=True, null=False)
    refresh_token = models.CharField(max_length=100, unique=True, null=False)
    claims = models.JSONField()
    expires = models.DateTimeField()


class OAuthAuthorizationCode(models.Model):
    client = models.ForeignKey(
        OAuthClient, null=False, on_delete=models.CASCADE)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    scopes = ArrayField(
        models.CharField(max_length=16, blank=False))
    redirect_uri = models.URLField(max_length=128, null=True)
    code = models.CharField(max_length=100, unique=True, null=False)
    code_state = models.CharField(max_length=100, null=True)
    challenge = models.CharField(max_length=128, null=True)
    challenge_method = models.CharField(max_length=6, null=True)
    claims = models.JSONField()
    expires = models.DateTimeField()


