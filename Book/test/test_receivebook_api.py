import datetime

from django.contrib.auth import get_user_model
from django.utils.timezone import get_current_timezone
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from Book.models import Book, BookRequest


class ReceiveBookTestCase(APITestCase):
    @classmethod
    def setUp(cls):
        # Create a user
        cls.donator_user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        cls.receiver_user = get_user_model().objects.create_user(
            email='receiver@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        cls.vip_donator = get_user_model().objects.create_user(
            email='vip@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789',
            is_vip=True,
            vip_end_date=datetime.datetime.now(tz=get_current_timezone()) + datetime.timedelta(days=30)
        )

        # Create test books
        cls.book1 = Book.objects.create(
            name='Book 1',
            description='Description 1',
            author='Author 1',
            is_donated=True,
            is_received=False,
            donator_id=cls.donator_user.pk,
        )

        # Create test books
        cls.book2 = Book.objects.create(
            name='Book 2',
            description='Description 2',
            author='Author 2',
            is_donated=True,
            donator_id=cls.vip_donator.pk,
        )

        # Create test books
        cls.book3 = Book.objects.create(
            name='Book 3',
            description='Description 3',
            author='Author 3',
            is_donated=False,
            donator_id=cls.donator_user.pk,
        )

        cls.book4 = Book.objects.create(
            name='Book 4',
            description='Description 4',
            author='Author 4',
            is_donated=True,
            is_received=True,
            donator_id=cls.donator_user.pk,
        )

        # Create book-request

        cls.url = '/book/request/receivebook/'


    def test_receive_book_should_mark_book_as_received_and_update_donator_rooyesh_and_credit(self):
        # Arrange
        data = {'book': self.book1.book_id}
        self.book_request_approved_and_book_not_received = BookRequest.objects.create(user=self.receiver_user,
                                                                                     book=self.book1, status=BookRequest.APPROVED,
                                                                                     is_reported=False)
        self.book_request_approved_and_book_not_received.save()

        # Act
        self.client.force_authenticate(user=self.receiver_user)
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertTrue(self.book1.is_received)
        self.donator_user.refresh_from_db()
        self.assertEqual(self.donator_user.rooyesh, 3 + 2)
        self.assertEqual(self.donator_user.credit, 1 + 2)

    def test_receive_book_vip_donator_should_mark_book_as_received_and_update_donator_rooyesh_and_add_extra_credit(self):
        # Arrange
        data = {'book': self.book2.book_id}
        self.book_request_approved_and_book_not_received = BookRequest.objects.create(user=self.receiver_user,
                                                                                     book=self.book2, status=BookRequest.APPROVED,
                                                                                     is_reported=False)
        self.book_request_approved_and_book_not_received.save()

        # Act
        self.client.force_authenticate(user=self.receiver_user)
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book2.refresh_from_db()
        self.assertTrue(self.book2.is_received)
        self.vip_donator.refresh_from_db()
        self.assertEqual(self.vip_donator.rooyesh, 3 + 2)
        self.assertEqual(self.vip_donator.credit, 1 + 3)


    def test_invalid_book_id_should_return_400(self):
        # Arrange
        data = {'book': 999}

        # Act
        self.client.force_authenticate(user=self.receiver_user)
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_donated_book_should_return_400(self):
        # Arrange
        data = {'book': self.book3.book_id}

        # Act
        self.client.force_authenticate(user=self.receiver_user)
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_book_already_received_should_return_400(self):
        # Arrange
        data = {'book': self.book4.book_id}
        self.book_request_approved_and_book_received = BookRequest.objects.create(user=self.receiver_user, book=self.book4, status=BookRequest.APPROVED, is_reported=False)

        # Act
        self.client.force_authenticate(user=self.receiver_user)
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_book_request_not_approved_should_return_400(self):
        # Arrange
        data = {'book': self.book1.book_id}
        self.book_request_not_approved = BookRequest.objects.create(user=self.receiver_user, book=self.book1, status=BookRequest.PENDING, is_reported=False)

        # Act
        self.client.force_authenticate(user=self.receiver_user)
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


