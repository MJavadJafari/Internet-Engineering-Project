from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotAcceptable
from rest_framework.exceptions import PermissionDenied


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        ref_name = 'UserSerializer'
        fields = ("email", "password", "first_name", "last_name", "user_id")

    email = serializers.EmailField(max_length=255, required=True)
    first_name = serializers.CharField(max_length=50, required=True)
    last_name = serializers.CharField(max_length=50, required=True)
    password = serializers.CharField(write_only=True, required=True)
    user_id = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("email exists.")
        return value


class UserInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        exclude = ('password', 'last_login', 'is_admin')
