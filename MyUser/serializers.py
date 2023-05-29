import random
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from MyUser.models import MyUser, EmailToken

import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("email", "password", "name", "user_id", "phone_number", "rooyesh")


    email = serializers.EmailField(max_length=255, required=True)
    rooyesh = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=50, required=True)
    password = serializers.CharField(write_only=True, required=True)
    phone_number = serializers.CharField(required=True)
    user_id = serializers.IntegerField(read_only=True)

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        token_for_email_validation = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
        EmailToken.objects.create(token=token_for_email_validation, user=user)
        user.is_active = False
        user.save()
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"UserSerializer.create: user = {user} created")
        send_mail(subject='تایید عضویت کهربا',
                  message='برای فعال سازی حساب کاربری خود بر روی لینک زیر کلیک کنید.'
                          + '\n' + self.context['request'].get_host() + '/auth/activate/' + token_for_email_validation + '\n',
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[user.email])
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"UserSerializer.create: activation email sent to {user.email}")
        return user

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("email exists.")

        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'phone_number', 'post_address')

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("email exists.")
        return value

    def update(self, instance, validated_data):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"UserUpdateSerializer.update: user = {instance}")
        if 'email' in validated_data:
            instance.is_active = False
            instance.email = validated_data.get('email')
            token_for_email_validation = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
            EmailToken.objects.create(token=token_for_email_validation, user=instance)
            instance.save()
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"UserUpdateSerializer.update: user {instance} email changed to {instance.email}")

            send_mail(subject='تایید عضویت کهربا',
                      message='برای فعال سازی حساب کاربری خود بر روی لینک زیر کلیک کنید.'
                              + '\n' + self.context[
                                  'request'].get_host() + '/auth/activate/' + token_for_email_validation + '\n',
                      from_email=settings.EMAIL_HOST_USER,
                      recipient_list=[instance.email])
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"UserUpdateSerializer.update: activation email sent to {instance.email}")

        instance.name = validated_data.get('name', instance.name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.post_address = validated_data.get('post_address', instance.post_address)
        instance.save()
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"UserUpdateSerializer.update: user {instance} updated, name = {instance.name}, phone_number = {instance.phone_number}, post_address = {instance.post_address}")
        return instance


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = ('password', 'last_login', 'is_admin', 'is_active')
