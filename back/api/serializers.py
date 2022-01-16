from django.contrib.auth import get_user_model

from rest_framework import serializers


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        user = User.objects.create_user(email, password, is_active=False)
        return user


class ServiceSerializer(serializers.ModelSerializer):
    pass


class ServiceVersionSerializer(serializers.ModelSerializer):
    pass
