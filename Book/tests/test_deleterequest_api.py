from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from Book.models import Book, BookRequest


class DeleteRequestTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        # Create a user
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        # Create test books
        cls.book1 = Book.objects.create(
            name='Book 1',
            description='Description 1',
            author='Author 1',
            is_donated=False,
            donator_id=cls.user.pk,
            created_at='2021-01-01'
        )

        # Create test books
        cls.book2 = Book.objects.create(
            name='Book 2',
            description='Description 2',
            author='Author 2',
            is_donated=True,
            donator_id=cls.user.pk,
            created_at='2021-01-01'
        )

        # Create test books
        cls.book3 = Book.objects.create(
            name='Book 3',
            description='Description 3',
            author='Author 3',
            is_donated=True,
            donator_id=cls.user.pk,
            created_at='2021-01-01'
        )
        cls.url = '/book/request/delete/'

    def test_delete_pending_request_from_not_donated_book_should_delete_request_and_increase_rooyesh(self):
        # Arrange
        data = {'book': self.book1.book_id}
        BookRequest.objects.create(user_id=self.user.pk, book_id=self.book1.pk, status=BookRequest.PENDING)
        self.user.rooyesh = 0
        self.user.save()

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BookRequest.objects.count(), 0)
        self.assertEqual(self.user.rooyesh, 1)


#     test for deleting a pending request from a donated book

    def test_delete_pending_request_from_donated_book_should_not_delete_request_and_not_increase_rooyesh(self):
        # Arrange
        data = {'book': self.book2.book_id}
        BookRequest.objects.create(user_id=self.user.pk, book_id=self.book2.pk, status=BookRequest.PENDING)
        self.user.rooyesh = 0
        self.user.save()

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BookRequest.objects.count(), 1)
        self.assertEqual(self.user.rooyesh, 0)

    #    test for deleting a accepted request from a donated book

    def test_delete_approved_request_from_donated_book_should_not_delete_request_and_not_increase_rooyesh(self):
        # Arrange
        data = {'book': self.book3.book_id}
        BookRequest.objects.create(user_id=self.user.pk, book_id=self.book3.pk, status=BookRequest.APPROVED)
        self.user.rooyesh = 0
        self.user.save()

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BookRequest.objects.count(), 1)
        self.assertEqual(self.user.rooyesh, 0)


    #    test for deleting a rejected request from a donated book

    def test_delete_rejected_request_from_donated_book_should_not_delete_request_and_not_increase_rooyesh(self):
        # Arrange
        data = {'book': self.book3.book_id}
        BookRequest.objects.create(user_id=self.user.pk, book_id=self.book3.pk, status=BookRequest.REJECTED)
        self.user.rooyesh = 0
        self.user.save()

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BookRequest.objects.count(), 1)
        self.assertEqual(self.user.rooyesh, 0)

    # test fot invalid book id
    def test_delete_request_with_invalid_book_id_should_not_delete_request_and_not_increase_rooyesh(self):
        # Arrange
        data = {'book': 100}
        BookRequest.objects.create(user_id=self.user.pk, book_id=self.book3.pk, status=BookRequest.PENDING)
        self.user.rooyesh = 0
        self.user.save()

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BookRequest.objects.count(), 1)
        self.assertEqual(self.user.rooyesh, 0)