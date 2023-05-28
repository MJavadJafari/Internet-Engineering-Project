from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Payment.models import Transaction


class PurchaseTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='abc',
            phone_number='123456789'
        )

        self.url = '/payment/request/'

    def test_pay_should_return_401_when_user_is_not_authenticated(self):
        # Act
        response = self.client.post(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_pay_should_return_400_when_duration_is_not_passed(self):
        # Arrange
        self.client.force_authenticate(user=self.user)

        # Act
        response = self.client.post(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_pay_should_return_400_when_duration_is_not_valid(self):
        # Arrange
        self.client.force_authenticate(user=self.user)

        # Act
        response = self.client.post(self.url, data={'duration': 100})

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)