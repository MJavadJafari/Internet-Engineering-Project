from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

class ChangePasswordTests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='abc',
            phone_number='123456789'
        )

        self.url = '/auth/change-password/'

    def tearDown(self) -> None:
        get_user_model().objects.all().delete()
        
        return super().tearDown()

    def test_change_password_should_return_success(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'testpassword',
            'new_password': 'newpassword'
        }

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'Success'})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword'))

    def test_change_password_should_return_401_when_user_is_not_authenticated(self):
        # Arrange
        self.client.force_authenticate(user=None)
        data = {
            'old_password': 'testpassword',
            'new_password': 'newpassword'
        }

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_change_password_should_return_400_when_old_password_is_wrong(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword'
        }

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'Wrong password'})

    def test_change_password_should_return_401_when_user_is_not_active(self):
        # Arrange
        self.user.is_active = False
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'testpassword',
            'new_password': 'newpassword'
        }

        # Act
        response = self.client.post(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        #refresh db
        self.user.refresh_from_db()
        self.assertEqual(response.data, {'User is not active'})

    