from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from MyUser.models import EmailToken
import random
import string

class ConfirmPasswordResetTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='abc',
            phone_number='123456789'
        )
        self.token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))
        self.email_token = EmailToken.objects.create(user=self.user, token=self.token)
        self.url = '/auth/confirm_password_reset/'

    def tearDown(self) -> None:
        get_user_model().objects.all().delete()
        EmailToken.objects.all().delete()

        return super().tearDown()

    def test_confirm_password_reset_should_render_form(self):
        # Arrange

        # Act
        response = self.client.get((f'{self.url}{self.token}'))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, 'password_reset_success.html')

    def test_confirm_password_reset_should_return_400_when_token_is_not_found(self):
        # Arrange
        token = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(30))

        # Act
        response = self.client.get((f'{self.url}{token}'))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'Invalid user'})
    
    def test_confirm_password_reset_should_return_400_when_token_is_empty(self):
        # Arrange
        token = ''

        # Act
        response = self.client.get((f'{self.url}{token}'))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_confirm_password_reset_should_change_old_password(self):
        # Arrange

        # Act
        response = self.client.get((f'{self.url}{self.token}'))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.user.check_password(self.user.password))