from django.contrib.auth import get_user_model

from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data['email']
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(
            email, password, username=username, is_active=False)
        return user


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username',)


class ServiceSerializer(serializers.ModelSerializer):
    pass


class ServiceVersionSerializer(serializers.ModelSerializer):
    pass


class OAuth2ClientSerializer(serializers.Serializer):
    user = PublicUserSerializer()
    client_name = serializers.CharField()
    website_uri = serializers.URLField()
    description = serializers.CharField()
    scope = serializers.ListField(child=serializers.CharField())


class OAuth2AuthzCodeSerializer(serializers.Serializer):
    client = OAuth2ClientSerializer()
