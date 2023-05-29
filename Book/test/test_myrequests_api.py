# # tests for myrequests api
# class My_requests(ListAPIView):
#     permission_classes = [
#         permissions.IsAuthenticated
#     ]
#     serializer_class = MyRequestsSerializer
#     filter_backends = (DjangoFilterBackend,)
#     filterset_fields = ['status']
#
#     def get_queryset(self):
#         return BookRequest.objects.filter(user=self.request.user)

from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Book.models import Book, BookRequest
from Book.serializers import AllBooksSerializer
from rest_framework.test import APIRequestFactory

class MyRequestsTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        cls.second_user = get_user_model().objects.create_user(
            email='second_user@example.com',
            password='testpassword',
            name='Second User',
            phone_number='123456789',
        )

        # Create test books
        cls.book1 = Book.objects.create(
            name='Book 1',
            description='Description 1',
            author='Author 1',
            is_donated=False,
            donator_id=cls.user.pk,
        )

        cls.book2 = Book.objects.create(
            name='Book 2',
            description='Description 2',
            author='Author 2',
            is_donated=False,
            donator_id=cls.second_user.pk,
        )

        cls.book3 = Book.objects.create(
            name='Book 3',
            description='Description 3',
            author='Author 3',
            is_donated=True,
            donator_id=cls.second_user.pk,
        )

        cls.url = '/book/request/myrequests/'

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_get_my_requests_should_return_all_my_requests(self):
        # Arrange
        BookRequest.objects.create(
            book=self.book1,
            user=self.user,
            status='PENDING',
            created_at='2021-01-01'
        )
        BookRequest.objects.create(
            book=self.book2,
            user=self.user,
            status='PENDING',
            created_at='2021-01-01'
        )

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


    def test_get_my_requests_should_return_only_my_requests(self):
        # Arrange
        BookRequest.objects.create(
            book=self.book1,
            user=self.user,
            status='PENDING',
            created_at='2021-01-01'
        )
        BookRequest.objects.create(
            book=self.book2,
            user=self.second_user,
            status='PENDING',
            created_at='2021-01-01'
        )

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user.pk)


    def test_get_approved_request_should_return_donator_phone_number_as_well(self):
        # Arrange
        BookRequest.objects.create(
            book=self.book3,
            user=self.user,
            status=BookRequest.APPROVED,
            created_at='2021-01-01'
        )

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['phone_number'], self.book3.donator.phone_number)


    def test_get_my_requests_should_return_only_my_requests_with_status(self):
        # Arrange
        BookRequest.objects.create(
            book=self.book1,
            user=self.user,
            status='PENDING',
            created_at='2021-01-01'
        )
        BookRequest.objects.create(
            book=self.book2,
            user=self.user,
            status='ACCEPTED',
            created_at='2021-01-01'
        )

        # Act
        response = self.client.get(self.url, {'status': 'PENDING'})

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['status'], 'PENDING')