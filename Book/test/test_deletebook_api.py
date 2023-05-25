from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Book.models import Book, BookRequest
from Book.serializers import AllBooksSerializer
from rest_framework.test import APIRequestFactory


class DeleteBookTests(APITestCase):

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
        # cls.book3 = Book.objects.create(


        cls.url = '/book/delete/'

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def test_delete_book_should_delete_book(self):
        # Arrange
        data = {
            'book': self.book1.pk
        }

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.get().name, 'Book 2')

    def test_delete_book_should_delete_book_requests_and_change_rooyesh(self):
        # Arrange
        data = {
            'book': self.book1.pk
        }
        # Create test book requests
        BookRequest.objects.create(user_id=self.second_user.pk, book_id=self.book1.pk)
        previous_rooyesh = self.second_user.rooyesh

        # Act
        response = self.client.post(self.url, data)
        self.second_user.refresh_from_db()

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BookRequest.objects.count(), 0)
        self.assertEqual(self.second_user.rooyesh, previous_rooyesh + 1)
        self.assertEqual(Book.objects.count(), 1)

    def test_delete_book_should_not_delete_book_if_not_donator(self):
        # Arrange
        data = {
            'book': self.book2.pk
        }

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 2)

    def test_delete_book_should_not_delete_book_if_book_does_not_exist(self):
        # Arrange
        data = {
            'book': 999
        }

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 2)

    def test_delete_book_should_not_delete_book_if_book_is_donated(self):
        # Arrange
        data = {
            'book': self.book1.pk
        }
        self.book1.is_donated = True
        self.book1.save()

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 2)

    def test_invalid_delete_should_not_delete_book_and_book_requests(self):
        # Arrange
        data = {
            'book': 'invalid'
        }
        BookRequest.objects.create(user_id=self.second_user.pk, book_id=self.book1.pk)
        previous_rooyesh = self.second_user.rooyesh

        # Act
        response = self.client.post(self.url, data)
        self.second_user.refresh_from_db()

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BookRequest.objects.count(), 1)
        self.assertEqual(self.second_user.rooyesh, previous_rooyesh)
        self.assertEqual(Book.objects.count(), 2)


