from rest_framework import serializers
from .models import SimpleUser
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimpleUser
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = SimpleUser(
            username=validated_data['username'],
            password=make_password(validated_data['password'])
        )
        user.save()
        return user

