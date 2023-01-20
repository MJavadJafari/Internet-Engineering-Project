from django.contrib.auth import get_user_model
from rest_framework import filters, permissions
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from Book.models import Book
from Book.serializers import BookSerializer


class RegisterBooks(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = BookSerializer


class AllBooks(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = BookSerializer

    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ['is_donated', 'donator']
    search_fields = ['name', 'description', 'author']

    queryset = Book.objects.all().order_by('-created_at')


class BookInfo(RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = BookSerializer
    queryset = Book.objects.all()

#
# class MyBooks(ListAPIView):
#     permission_classes = [
#         permissions.IsAuthenticated
#     ]
#     serializer_class = BookSerializer
#
#     def get_queryset(self):
#         return Book.objects.filter(donator=self.request.user).order_by('-created_at')


