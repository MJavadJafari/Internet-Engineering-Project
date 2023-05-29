from rest_framework import status
from rest_framework.test import APITestCase, force_authenticate
from django.contrib.auth import get_user_model
from Book.models import Book, BookRequest
from Book.serializers import AllBooksSerializer
from rest_framework.test import APIRequestFactory

class AllBooksTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        self.book1 = Book.objects.create(
            name='Book 1',
            description='Description 1',
            author='Author 1',
            is_donated=True,
            donator_id=self.user.pk,
        )

        # Create test books
        self.book2 = Book.objects.create(
            name='Book 2',
            description='Description 2',
            author='Author 2',
            is_donated=True,
            donator_id=self.user.pk,
        )

        self.book3 = Book.objects.create(
            name='Book 3',
            description='Description 3',
            author='Author 3',
            is_donated=True,
            donator_id=self.user.pk,
        )

        self.book4 = Book.objects.create(
            name='Book 4',
            description='Description 4',
            author='Author 4',
            is_donated=False,
            donator_id=self.user.pk,
        )

        # Create book-request
        self.book_request_approved_and_not_reported = BookRequest.objects.create(user=self.user, book=self.book1, status=BookRequest.APPROVED, is_reported=False)
        self.book_request_approved_and_reported = BookRequest.objects.create(user=self.user, book=self.book2, status=BookRequest.APPROVED, is_reported=True)
        self.book_request_pending = BookRequest.objects.create(user=self.user, book=self.book3, status=BookRequest.PENDING, is_reported=False)
        self.book_request_not_donated_book = BookRequest.objects.create(user=self.user, book=self.book4, status=BookRequest.APPROVED, is_reported=False)
        self.url = '/book/request/report/'

        self.book1.refresh_from_db()
        self.book2.refresh_from_db()
        self.book3.refresh_from_db()
        self.book_request_approved_and_not_reported.refresh_from_db()
        self.book_request_approved_and_reported.refresh_from_db()
        self.book_request_pending.refresh_from_db()
        self.client.force_authenticate(user=self.user)

    def tearDown(self) -> None:
        Book.objects.all().delete()
        BookRequest.objects.all().delete()
        get_user_model().objects.all().delete()

        return super().tearDown()

    def test_valid_report_request_should_mark_request_as_reported(self):
        # Arrange
        data = {'book': self.book1.book_id}

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.book_request_approved_and_reported.is_reported)

    def test_already_reported_request_should_return_bad_request(self):
        # Arrange
        data = {'book': self.book2.book_id}

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(self.book_request_approved_and_reported.is_reported)

    def test_pending_request_should_return_bad_request(self):
        # Arrange
        data = {'book': self.book3.book_id}

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(self.book_request_pending.is_reported)

    def test_report_request_with_no_data_should_return_bad_request(self):
        # Arrange
        data = {}

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_report_request_with_no_book_id_should_return_bad_request(self):
        # Arrange
        data = {'book': ''}

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_report_request_with_invalid_book_id_should_return_bad_request(self):
        # Arrange
        data = {'book': 100}

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_report_not_donated_book_should_return_bad_request(self):
        # Arrange
        data = {'book': self.book4.book_id}

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_user_should_return_unauthorized(self):
        # Arrange
        data = {'book': self.book1.book_id}

        # Act
        self.client.logout()
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
