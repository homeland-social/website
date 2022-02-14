from django.contrib.auth import get_user_model

from rest_framework import serializers
from drf_recaptcha.fields import ReCaptchaV2Field

from api.models import SSHKey, Hostname, OAuth2Token


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'recaptcha')
        extra_kwargs = {
            'password': {'write_only': True},
            'recaptcha': {'write_only': True},
        }

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

    def __init__(self, pk, *args, **kwargs):
        self.pk = pk
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        try:
            user = User.objects.get(pk=self.pk)
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid signature')
        try:
            user.validate_confirmation(attrs['ts'], attrs['signature'])

        except ValueError as e:
            raise serializers.ValidationError('Invalid signature')
        return attrs

    def create(self, validated_data):
        user = User.objects.get(pk=self.pk)
        user.is_active = True
        user.is_confirmed = True
        return user


class OAuth2ClientSerializer(serializers.Serializer):
    user = UserSerializer(fields=('username',))
    client_name = serializers.CharField()
    website_uri = serializers.URLField()
    description = serializers.CharField()
    scope = serializers.ListField(child=serializers.CharField())


class OAuth2TokenSerializer(serializers.Serializer):
    class Meta:
        model = OAuth2Token
        fields = ('client', 'token_type', 'scope', 'revoked', 'issued_at', 'expires_in')

    client = OAuth2ClientSerializer()


class OAuth2AuthzCodeSerializer(serializers.Serializer):
    client = OAuth2ClientSerializer()


class SSHKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = SSHKey
        fields = ('name', 'key', 'type', 'created', 'modified')


class HostnameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostname
        fields = ('name',)
