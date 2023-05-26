from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

class ResetPasswordTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # create user
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='abc',
            phone_number='123456789'
        )

        cls.url = '/auth/reset-password/'

    
    def test_reset_password_should_return_success(self):
        # Arrange
        data = {
            'email': self.user.email,
        }

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'Success'})

    
    def test_reset_password_should_return_400_when_email_is_not_found(self):
        # Arrange
        data = {
            'email': 'notfound@email.com',
        }

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'Invalid user'})

    def test_reset_password_should_return_400_when_email_is_empty(self):
        # Arrange
        data = {
            'email': '',
        }

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'Invalid user'})
