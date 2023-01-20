from django.contrib.auth import get_user_model
from rest_framework import permissions
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView

from Book.models import Book
from Book.serializers import BookSerializer


class RegisterBooks(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = BookSerializer


class ActiveBooks(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = BookSerializer
    queryset = Book.objects.filter(is_donated=False)


class BookInfo(RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = BookSerializer
    queryset = Book.objects.all()


class MyBooks(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.filter(donator=self.request.user)


