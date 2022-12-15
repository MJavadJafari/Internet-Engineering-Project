from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, RetrieveAPIView

from Book.models import Book
from Book.serializers import BookSerializer
from MyUser.serializers import UserSerializer, UserInfoSerializer


class RegisterBooks(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = BookSerializer


class BookInfo(RetrieveAPIView):
    permission_classes = [
        permissions.AllowAny
    ]
    serializer_class = BookSerializer
    queryset = Book.objects.all()

    # def get_object(self):
    #     return self.request.user
