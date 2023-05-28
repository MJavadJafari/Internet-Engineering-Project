from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from MyUser.models import EmailToken
import random
import string

class ActivateUserTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # create user
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='abc',
            phone_number='123456789'
        )
        cls.token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        cls.email_token = EmailToken.objects.create(user=cls.user, token=cls.token)
        cls.url = '/auth/activate/'

    def test_activate_user_should_return_success_form(self):
        # Arrang
        self.user.is_active = False

        # Act
        response = self.client.get((f'{self.url}{self.token}'))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)
        self.assertFalse(EmailToken.objects.filter(token=self.email_token.token).exists())
        self.assertTemplateUsed(response, 'activation_success.html')

    def test_activate_user_should_return_400_when_token_is_not_found(self):
        # Arrange
        self.user.is_active = False

        # Act
        token = 'wrongToken'
        response = self.client.get((f'{self.url}{token}'))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'Invalid user'})

    def test_activate_user_should_return_404_when_token_is_empty(self):
        # Arrange
        token = ''

        # Act
        response = self.client.get((f'{self.url}{token}'))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
