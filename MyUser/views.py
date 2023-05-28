import random
import string

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils import timezone
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView

from MyUser.models import EmailToken, MyUser
from MyUser.permissions import OwnProfilePermission
from MyUser.serializers import UserSerializer, UserInfoSerializer, UserUpdateSerializer

import logging

logger = logging.getLogger(__name__)

class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        # log in format [time] [level] [message]
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "CustomAuthToken.post")
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"CustomAuthToken.post: user = {user} logged in")

        # if vip_end_date is passed, make user not vip.check for None because it can be null
        user.update_vip_status()

        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"CustomAuthToken.post: user = {user} vip_end_date = {user.vip_end_date}")
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"CustomAuthToken.post: user = {user} response = {Response}")
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'name': user.name,
            'phone_number': user.phone_number,
            'rooyesh': user.rooyesh
        })


class RegisterUsers(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "RegisterUsers.create")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"RegisterUsers.create: user = {serializer.instance} response = 200")
        return Response({'Success'}, status=HTTP_200_OK)


class UserInfo(RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        OwnProfilePermission
    ]
    serializer_class = UserInfoSerializer

    def get_object(self):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"UserInfo.get_object: user = {self.request.user}")
        return self.request.user


class UpdateUser(UpdateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        OwnProfilePermission
    ]
    serializer_class = UserUpdateSerializer

    def get_object(self):
        return self.request.user


# change password
class ChangePassword(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        OwnProfilePermission
    ]

    def post(self, request):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "ChangePassword.post")
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        if not old_password or not new_password:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "ChangePassword.post: invalid data, response = 400")
            return Response({'Invalid data'}, status=HTTP_400_BAD_REQUEST)
        
        # check if user is active
        if not user.is_active:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "ChangePassword.post: user is not active, response = 400")
            return Response({'User is not active'}, status=HTTP_400_BAD_REQUEST)
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"ChangePassword.post: user = {user} password changed")
            return Response({'Success'}, status=HTTP_200_OK)
        else:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "ChangePassword.post: wrong password, response = 400")
            return Response({'Wrong password'}, status=HTTP_400_BAD_REQUEST)


# password reset
class PasswordReset(APIView):
    def post(self, request):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "PasswordReset.post")
        email = request.data.get('email')
        try:
            user = MyUser.objects.get(email=email)
        except:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "PasswordReset.post: invalid user, response = 400")
            return Response({'Invalid user'}, status=HTTP_400_BAD_REQUEST)

        # generate token
        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))

        # save token
        email_token = EmailToken.objects.create(user=user, token=token)

        # send link to reset password
        send_mail(subject='بازیابی رمز عبور کهربا',
                  message='لینک بازیابی رمز عبور: ' + '\n' +
                          request.get_host() + '/auth/confirm_password_reset/' + token + '\n',
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[user.email])

        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"PasswordReset.post: user = {user} email sent")
        return Response({'Success'}, status=HTTP_200_OK)


# confirm password reset
class ConfirmPasswordReset(APIView):
    def get(self, request, token):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "ConfirmPasswordReset.get")
        try:
            email_token = EmailToken.objects.get(token=token)
            user = email_token.user
        except:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "ConfirmPasswordReset.get: invalid user, response = 400")
            return Response({'Invalid user'}, status=HTTP_400_BAD_REQUEST)

        # generate new password
        new_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))

        # set new password
        user.set_password(new_password)
        user.save()
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"ConfirmPasswordReset.get: user = {user} password changed")

        send_mail(subject='بازیابی رمز عبور کهربا',
                  message='رمز حساب کاربری شما با موفقیت بازنشانی شد. برای ورود به سامانه از رمز عبور زیر استفاده کنید.'
                          + '\n' + 'رمز عبور: ' + new_password + '\n',
                  from_email=settings.EMAIL_HOST_USER,
                  recipient_list=[user.email])
        
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"ConfirmPasswordReset.get: user = {user} email sent")

        email_token.delete()
        return render(request, 'password_reset_success.html')


class ActivateUser(APIView):
    def get(self, request, token):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "ActivateUser.get")
        try:
            email_token = EmailToken.objects.get(token=token)
            user = email_token.user
        except:
            logger.error("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.ERROR), "ActivateUser.get: invalid user, response = 400")
            return Response({'Invalid user'}, status=HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save()

        email_token.delete()
        
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"ActivateUser.get: user = {user} activated")
        return render(request, 'activation_success.html')

