from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth import get_user_model

from Book.models import BookRequest


class AddRequestTests(APITestCase):

    def setUpClass(cls):
        super().setUpClass()

        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def make_request(self, data):
        url = '/book/request/register/'
        response = self.client.post(url, data, format='json')
        return response

    def test_add_request_should_create_request(self):
        # Arrange
        data = {
            'user': self.user.pk,
            'book': 1,
            'status': 'Pending',
            'is_reported': False
        }

        # Act
        response = self.make_request(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookRequest.objects.count(), 1)
        self.assertEqual(BookRequest.objects.first().user, self.user)
        self.assertEqual(BookRequest.objects.first().book_id, 1)

    def test_add_request_with_existing_request_should_return_existing_request(self):
        # Arrange
        existing_request = BookRequest.objects.create(
            user=self.user,
            book_id=1,
            status='Pending',
            is_reported=False
        )

        data = {
            'user': self.user.pk,
            'book': 1,
            'status': 'Pending',
            'is_reported': False
        }

        # Act
        response = self.make_request(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(BookRequest.objects.count(), 1)
        self.assertEqual(BookRequest.objects.first().id, existing_request.id)

    def test_add_request_without_enough_rooyesh_should_return_error(self):
        # Arrange
        self.user.rooyesh = 0
        self.user.save()

        data = {
            'user': self.user.pk,
            'book': 1,
            'status': 'Pending',
            'is_reported': False
        }

        # Act
        response = self.make_request(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Not enough rooyesh')
        self.assertEqual(BookRequest.objects.count(), 0)
