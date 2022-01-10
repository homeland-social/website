from pkg_resources import parse_version

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager


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
        url = reverse('api_users_confirm')
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
        User.objects.filter(pk=self.pk).update(is_confirmed=True)
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
        ServiceVersion, related_name='conflicts_with', on_delete=models.CASCADE)


