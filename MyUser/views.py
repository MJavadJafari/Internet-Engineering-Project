from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, RetrieveAPIView

from MyUser.permissions import OwnProfilePermission
from MyUser.serializers import UserSerializer, UserInfoSerializer


class RegisterUsers(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = UserSerializer


class UserInfo(RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        OwnProfilePermission
    ]
    serializer_class = UserInfoSerializer

    def get_object(self):
        return self.request.user
