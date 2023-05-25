import random
import requests
from django.conf import Settings, settings

from django.contrib.auth import get_user_model
from rest_framework import filters, permissions
from rest_framework.generics import CreateAPIView, RetrieveAPIView, ListAPIView, GenericAPIView, UpdateAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework.views import APIView

from Book.models import Book, BookRequest
from Book.serializers import BookSerializer, BookRequestSerializer, MyRequestsSerializer, AllBooksSerializer
from MyUser.models import MyUser


class RegisterBooks(CreateAPIView):
    model = get_user_model()
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = BookSerializer


class BookInfoWithSuggestion(APIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request, pk):
        try:
            book = Book.objects.get(book_id=pk)
        except:
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)
        
        req = {
            'id' : book.book_id,
        }

        try:
            res = requests.post(settings.FLASK_SERVER_ADDRESS + '/ask_book', data=req)
            if res.status_code == 200:
                similar_books = Book.objects.filter(book_id__in=res.json())
            else:
                similar_books = Book.objects.all().exclude(book_id=book.book_id).order_by('?')[:5]
        except:
            similar_books = Book.objects.all().exclude(book_id=book.book_id).order_by('?')[:5]

        response = {
            "book": AllBooksSerializer(book, context={'request': request}).data,
            "similar_books": AllBooksSerializer(similar_books, many=True, context={'request': request}).data,
        }
        return Response(response, status=HTTP_200_OK)


class AllBooks(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = AllBooksSerializer

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


class My_requests(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = MyRequestsSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['status']

    def get_queryset(self):
        return BookRequest.objects.filter(user=self.request.user)


class ConfirmDonate(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        print(request.data)
        try:
            book = Book.objects.get(is_donated=False, donator=self.request.user, book_id=request.data['book'])
        except:
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        all_requests = BookRequest.objects.filter(book=book)
        registered_users = MyUser.objects.filter(user_id__in=all_requests.values_list('user'))
        if len(registered_users) == 0:
            return Response({"No one signed up yet"}, status=HTTP_400_BAD_REQUEST)

        registered_users = list(registered_users)
        random_weights = [x.credit * 1.1 if x.is_user_vip() else x.credit for x in registered_users]
        chosen_user = random.choices(registered_users, weights=random_weights, k=1)[0]

        # set request status
        for req in all_requests:
            if req.user == chosen_user:
                req.status = BookRequest.APPROVED
            else:
                req.status = BookRequest.REJECTED

            req.save()

        # set book donated
        book.is_donated = True
        book.save()

        return Response({"phone_number": chosen_user.phone_number,
                         "name": chosen_user.name,
                         "post_address": chosen_user.post_address}, status=HTTP_200_OK)


class DeleteBook(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        try:
            book = Book.objects.get(is_donated=False, donator=self.request.user, book_id=request.data['book'])
        except:
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        all_requests = BookRequest.objects.filter(book=book)
        registered_users = MyUser.objects.filter(user_id__in=all_requests.values_list('user'))

        # return rooyesh
        for user in registered_users:
            if user != self.request.user:
                user.change_rooyesh(1)
                user.save(update_fields=['rooyesh'])

        # delete request
        for req in all_requests:
            req.delete()

        book.delete()

        return Response({'Success'}, status=HTTP_200_OK)


class DeleteRequest(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        try:
            book = Book.objects.get(is_donated=False, book_id=request.data['book'])
            req = BookRequest.objects.get(user=self.request.user, book=book, status=BookRequest.PENDING)
        except:
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        self.request.user.change_rooyesh(1)
        req.delete()
        return Response({'Success'}, status=HTTP_200_OK)


class ReportRequest(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        try:
            book = Book.objects.get(is_donated=True, book_id=request.data['book'])
            req = BookRequest.objects.get(user=self.request.user, book=book, status=BookRequest.APPROVED,
                                          is_reported=False)
        except:
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        req.is_reported = True
        req.save()
        return Response({'Success'}, status=HTTP_200_OK)


class ReceiveBook(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        try:
            book = Book.objects.get(is_donated=True, book_id=request.data['book'], is_received=False)
            req = BookRequest.objects.get(user=self.request.user, book=book, status=BookRequest.APPROVED)
        except:
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        book.is_received = True
        book.save()

        donator = book.donator
        number_of_request = book.number_of_request
        donator.change_rooyesh((number_of_request/30) + 2)

        is_donator_vip = donator.is_user_vip()
        if is_donator_vip:
            donator.change_credit(3)
        else:
            donator.change_credit(2)
        donator.save()
        return Response({'Success'}, status=HTTP_200_OK)
