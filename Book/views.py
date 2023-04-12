import random

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


class AllBooks(ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated
    ]
    serializer_class = AllBooksSerializer

    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    filterset_fields = ['is_donated', 'donator']
    search_fields = ['name', 'description', 'author']

    queryset = Book.objects.all().order_by('-created_at')

    def get_queryset(self):
        # try:
        #     from Recommender.Recommender import SingletonRecommender
        #     for book in Book.objects.all():
        #         book.ranking = 0
        #         book.save()
        #     book = BookRequest.objects.filter(user=self.request.user).order_by('-created_at')[0]
        #     rec = SingletonRecommender()
        #     ans = rec.ask_book(book.book_id)
        #     for i in range(len(ans)):
        #         x = Book.objects.get(book_id=ans[i])
        #         x.ranking = len(ans) - i
        #         x.save()
        #     return Book.objects.all().order_by('-ranking', '-created_at')
        # except Exception as e:
        #     print(e)
        # TODO: add ranking
        return Book.objects.all().order_by('-created_at')


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
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ['book', 'status']

    def get_queryset(self):
        return BookRequest.objects.filter(book__donator=self.request.user)


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

        print(registered_users)
        # return rooyesh
        for user in registered_users:
            if user != self.request.user:
                user.change_rooyesh(1)

        # delete request
        for req in all_requests:
            req.delete()

        # delete book
        # try:
        #     from Recommender.Recommender import SingletonRecommender
        #     rec = SingletonRecommender()
        #     rec.delete_book(book.book_id)
        # except Exception as e:
        #     print(e)
        # TODO: delete book from recommender
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
