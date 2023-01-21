from django.contrib.auth import get_user_model
from rest_framework import filters, permissions
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, GenericAPIView
from django_filters.rest_framework import DjangoFilterBackend
from Book.models import Book, BookRequest
from Book.permissions import RequestPermission
from Book.serializers import BookSerializer, BookRequestSerializer


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


class AddRequest(CreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = BookRequestSerializer


class Requests_to_me(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = BookRequestSerializer
    queryset = BookRequest.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['book', 'status']
    
    def get_queryset(self):
        return BookRequest.objects.filter(user=self.request.user)
#
# class MyBooks(ListAPIView):
#     permission_classes = [
#         permissions.IsAuthenticated
#     ]
#     serializer_class = BookSerializer
#
#     def get_queryset(self):
#         return Book.objects.filter(donator=self.request.user).order_by('-created_at')


