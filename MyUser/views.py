from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.response import Response

from MyUser.permissions import OwnProfilePermission
from MyUser.serializers import UserSerializer, UserInfoSerializer


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
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


class UserInfo(RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        OwnProfilePermission
    ]
    serializer_class = UserInfoSerializer

    def get_object(self):
        return self.request.user
