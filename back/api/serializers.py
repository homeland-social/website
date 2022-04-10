from django.contrib.auth import get_user_model

from rest_framework import serializers
from drf_recaptcha.fields import ReCaptchaV2Field

from api.models import (
    SSHKey, Hostname, OAuth2Token, OAuth2Client, OAuth2Code, Console,
)


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('uid', 'username', 'email', 'password', 'recaptcha')
        extra_kwargs = {
            'password': {'write_only': True},
            'recaptcha': {'write_only': True},
        }

    uid = serializers.CharField(read_only=True)
    recaptcha = ReCaptchaV2Field()

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def create(self, validated_data):
        kwargs = {
            k: v for k, v in validated_data.items() if k != 'recaptcha'
        }
        return User.objects.create_user(is_active=False, **kwargs)


class UserConfirmSerializer(serializers.Serializer):
    ts = serializers.FloatField()
    signature = serializers.CharField()

    def __init__(self, uid, *args, **kwargs):
        self.uid = uid
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        try:
            user = User.objects.get(uid=self.uid)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid signature')
        try:
            user.validate_confirmation(attrs['ts'], attrs['signature'])

        except ValueError as e:
            raise serializers.ValidationError('Invalid signature')
        return attrs

    def create(self, validated_data):
        user = User.objects.get(uid=self.uid)
        user.is_active = True
        user.is_confirmed = True
        return user


class OAuth2ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuth2Client
        fields = ('user', 'client_id', 'client_name', 'website_uri', 'description', 'scope')

    user = UserSerializer(fields=('uid', 'username',))


class OAuth2TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = OAuth2Token
        fields = ('uid', 'client', 'token_type', 'scope', 'revoked',
                  'issued_at', 'expires_in')

    uid = serializers.CharField(read_only=True)
    client = OAuth2ClientSerializer()


class OAuth2AuthzCodeSerializer(serializers.Serializer):
    client = OAuth2ClientSerializer()


class SSHKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = SSHKey
        fields = ('uid', 'name', 'key', 'type', 'created', 'modified')

    uid = serializers.CharField(read_only=True)


class HostnameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostname
        fields = ('uid', 'name', 'internal', 'addresses', 'created', 'modified')

    uid = serializers.CharField(read_only=True)
    internal = serializers.BooleanField(read_only=True)


class ConsoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Console
        fields = ('uuid', 'token', 'created', 'used', 'sshkeys', 'hosts')

    sshkeys = SSHKeySerializer(many=True)
    hosts = HostnameSerializer(many=True)
