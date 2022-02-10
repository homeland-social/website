from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework_recaptcha.fields import ReCaptchaField

from api.models import SSHKey


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'recaptcha')
        extra_kwargs = {
            'password': {'write_only': True},
            'recaptcha': {'write_only': True},
        }

    recaptcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

    def create(self, validated_data):
        username = validated_data['email']
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(
            email, password, username=username, is_active=False)
        return user


class OAuth2ClientSerializer(serializers.Serializer):
    user = UserSerializer(fields=('username',))
    client_name = serializers.CharField()
    website_uri = serializers.URLField()
    description = serializers.CharField()
    scope = serializers.ListField(child=serializers.CharField())


class OAuth2AuthzCodeSerializer(serializers.Serializer):
    client = OAuth2ClientSerializer()


class SSHKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = SSHKey
        fields = ('name', 'key', 'type', 'created', 'modified')
