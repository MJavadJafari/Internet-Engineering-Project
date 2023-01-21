from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name", "user_id", "phone_number", "token", "rooyesh")

    email = serializers.EmailField(max_length=255, required=True)
    rooyesh = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50, required=True)
    password = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)
    user_id = serializers.IntegerField(read_only=True)
    token = serializers.SerializerMethodField(method_name='get_token', read_only=True)

    def get_token(self, user):
        return Token.objects.get_or_create(user=user)[0].key

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
        exclude = ('password', 'last_login', 'is_admin', 'is_active')
