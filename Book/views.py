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
from django.apps import apps
from importlib import import_module


from Book.models import Book, BookRequest
from Book.serializers import BookSerializer, BookRequestSerializer, MyRequestsSerializer, AllBooksSerializer
from Book.user_selection_strategy.random_user_selection import RandomUserSelectionStrategy
from Book.user_selection_strategy.weighted_random_user_selection import WeightedRandomUserSelectionStrategy
from Book.utils.confirm_donate_util import ConfirmDonateUtil
from MyUser.models import MyUser
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


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
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "BookInfoWithSuggestion.get")
        try:
            book = Book.objects.get(book_id=pk)
        except:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "BookInfoWithSuggestion.get: book not found, response = 400")
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        req = {
            'id': book.book_id,
        }

        if settings.USE_FLASK_SERVER:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "BookInfoWithSuggestion.get: using flask server")
            try:
                res = requests.post(settings.FLASK_SERVER_ADDRESS + '/ask_book', data=req)
                if res.status_code == 200:
                    logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "BookInfoWithSuggestion.get: flask server respended with 200, using similar books provided by flask server")
                    similar_books = Book.objects.filter(book_id__in=res.json())
                else:
                    logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "BookInfoWithSuggestion.get: flask server respended with 400, using random similar books")
                    similar_books = Book.objects.filter(is_donated=False).exclude(book_id=book.book_id).order_by('?')[:5]
            except:
                logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "BookInfoWithSuggestion.get: flask server not found, using random similar books")
                similar_books = Book.objects.filter(is_donated=False).exclude(book_id=book.book_id).order_by('?')[:5]
        else:
            similar_books = Book.objects.filter(is_donated=False).exclude(book_id=book.book_id).order_by('?')[:5]

        response = {
            "book": AllBooksSerializer(book, context={'request': request}).data,
            "similar_books": AllBooksSerializer(similar_books, many=True, context={'request': request}).data,
        }
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"BookInfoWithSuggestion.get: user {request.user} got book info with suggestion, response = 200")
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

    confirmation_util = ConfirmDonateUtil(settings.USER_SELECTION_STRATEGY)

    def post(self, request):
        return self.confirmation_util.confirm_donate(request)


class DeleteBook(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "DeleteBook.post")
        try:
            book = Book.objects.get(is_donated=False, donator=self.request.user, book_id=request.data['book'])
        except:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "DeleteBook.post: user {self.request.user}, book not found, response = 400")
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        all_requests = BookRequest.objects.filter(book=book)
        registered_users = MyUser.objects.filter(user_id__in=all_requests.values_list('user'))

        # return rooyesh
        for user in registered_users:
            if user != self.request.user:
                user.change_rooyesh(1)
                user.save(update_fields=['rooyesh'])
                logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"DeleteBook.post: user {user} rooyesh changed to {user.rooyesh}")

        # delete request
        for req in all_requests:
            req.delete()
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"DeleteBook.post: request with user {req.user} and book {req.book} deleted")

        book.delete()
        
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"DeleteBook.post: user {self.request.user}, book {book} deleted")
        return Response({'Success'}, status=HTTP_200_OK)


class DeleteRequest(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "DeleteRequest.post")
        try:
            book = Book.objects.get(is_donated=False, book_id=request.data['book'])
            req = BookRequest.objects.get(user=self.request.user, book=book, status=BookRequest.PENDING)
        except:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "DeleteRequest.post: user {self.request.user}, book not found, response = 400")
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        self.request.user.change_rooyesh(1)
        req.delete()
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"DeleteRequest.post: user {self.request.user}, request with user {req.user} and book {req.book} deleted")
        return Response({'Success'}, status=HTTP_200_OK)


class ReportRequest(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "ReportRequest.post")
        try:
            book = Book.objects.get(is_donated=True, book_id=request.data['book'])
            req = BookRequest.objects.get(user=self.request.user, book=book, status=BookRequest.APPROVED,
                                          is_reported=False)
        except:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "ReportRequest.post: user {self.request.user}, book not found, response = 400")
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        req.is_reported = True
        req.save()
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"ReportRequest.post: user {self.request.user}, request with user {req.user} and book {req.book} reported")
        return Response({'Success'}, status=HTTP_200_OK)


class ReceiveBook(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def post(self, request):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "ReceiveBook.post")
        try:
            book = Book.objects.get(is_donated=True, book_id=request.data['book'], is_received=False)
            req = BookRequest.objects.get(user=self.request.user, book=book, status=BookRequest.APPROVED)
        except:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "ReceiveBook.post: user {self.request.user}, book not found, response = 400")
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        book.is_received = True
        book.save()

        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"ReceiveBook.post: user {self.request.user}, book {book} set to received")

        donator = book.donator
        number_of_request = book.number_of_request
        donator.change_rooyesh((number_of_request / 30) + 2)

        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"ReceiveBook.post: user {donator}, rooyesh changed to {donator.rooyesh}")

        is_donator_vip = donator.is_user_vip()
        if is_donator_vip:
            donator.change_credit(3)
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"ReceiveBook.post: user {donator}, is vip, credit changed to {donator.credit}")
        else:
            donator.change_credit(2)
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"ReceiveBook.post: user {donator}, is not vip, credit changed to {donator.credit}")
        donator.save()
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"ReceiveBook.post: user {donator}, response = 200")
        return Response({'Success'}, status=HTTP_200_OK)
