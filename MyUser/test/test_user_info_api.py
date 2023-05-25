from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Book.models import Book, BookRequest
from Book.serializers import AllBooksSerializer
from rest_framework.test import APIRequestFactory


class UserInfoTests(APITestCase):
    
    @classmethod
    def setUpTestData(cls):
        # create user
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='abc',
            phone_number='123456789'
        )

        cls.url = '/auth/info/'

    def test_get_user_info(self):
        # Arrange
        self.client.force_authenticate(user=self.user)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = {
            'user_id': self.user.user_id,
            'email': self.user.email,
            'name': self.user.name,
            'phone_number': self.user.phone_number,
            'credit': self.user.credit,
            'rooyesh': self.user.rooyesh,
            'post_address': self.user.post_address,
            'is_vip': self.user.is_vip,
            'vip_end_date': self.user.vip_end_date
        }
        self.assertEqual(response.data, expected_data)

    def test_get_user_info_should_return_401_when_user_is_not_authenticated(self):
        # Arrange
        self.client.force_authenticate(user=None)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

