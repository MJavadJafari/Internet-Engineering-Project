from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Payment.models import Transaction

class VIPOptionsTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='abc',
            phone_number='123456789'
        )

        self.url = '/payment/options/'

    def tearDown(self) -> None:
        get_user_model().objects.all().delete()
        Transaction.objects.all().delete()
        
        return super().tearDown()

    def test_get_vip_options_should_return_401_when_user_is_not_authenticated(self):
        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_vip_options_should_return_200_when_user_is_authenticated(self):
        # Arrange
        self.client.force_authenticate(user=self.user)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, Transaction.VIP_OPTIONS)
        