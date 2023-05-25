from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Book.models import Book, BookRequest
from Book.serializers import AllBooksSerializer
from rest_framework.test import APIRequestFactory


class UpdateUserTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # create user
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='abc',
            phone_number='123456789'
        )
        cls.user2 = get_user_model().objects.create_user(
            email='exsisting@email.com',
            password='testpassword',
            name='abc',
            phone_number='123456789'
        )

        cls.url = '/auth/update/'

    def test_update_user_info(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'new name',
            'phone_number': '987654321',
            'post_address': 'new post address'
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'new name')
        self.assertEqual(self.user.phone_number, '987654321')
        self.assertEqual(self.user.post_address, 'new post address')

    def test_update_user_info_should_return_401_when_user_is_not_authenticated(self):
        # Arrange
        self.client.force_authenticate(user=None)
        data = {
            'name': 'new name',
            'phone_number': '987654321',
            'post_address': 'new post address'
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')

    def test_update_user_info_should_return_200_when_name_is_not_provided(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'phone_number': '987654321',
            'post_address': 'new post address'
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'abc')
        self.assertEqual(self.user.phone_number, '987654321')
        self.assertEqual(self.user.post_address, 'new post address')

    def test_update_user_info_should_return_200_when_phone_number_is_not_provided(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'new name',
            'post_address': 'new post address'
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'new name')
        self.assertEqual(self.user.phone_number, '123456789')
        self.assertEqual(self.user.post_address, 'new post address')

    def test_update_user_info_should_return_200_when_post_address_is_not_provided(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'new name',
            'phone_number': '987654321',
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'new name')
        self.assertEqual(self.user.phone_number, '987654321')
        self.assertEqual(self.user.post_address, '')

    def test_update_user_info_should_return_200_when_all_fields_are_not_provided(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {}

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'abc')
        self.assertEqual(self.user.phone_number, '123456789')
        self.assertEqual(self.user.post_address, '')    

    def test_update_user_email(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'email': 'new@email.com',
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, data['email'])
        self.assertEqual(self.user.name, 'abc')
        self.assertEqual(self.user.phone_number, '123456789')
        self.assertEqual(self.user.post_address, '')
        self.assertEqual(self.user.is_active, False)

    def test_update_user_email_should_return_400_with_existing_email(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'email':'exsisting@email.com',
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'my user with this email already exists.')

    def test_update_user_email_should_return_400_with_invalid_email(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'email':'invalidemail',
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'Enter a valid email address.')

    def test_update_user_email_should_return_400_with_empty_email(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'email':'',
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field may not be blank.')

    def test_update_user_email_should_return_400_with_invalid_email_and_other_fields(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'email':'invalidemail',
            'name': 'new name',
            'phone_number': '987654321',
            'post_address': 'new post address'
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'Enter a valid email address.')

    def test_update_user_email_should_return_400_with_empty_email_and_other_fields(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'email':'',
            'name': 'new name',
            'phone_number': '987654321',
            'post_address': 'new post address'
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field may not be blank.')

    def test_update_user_email_should_return_400_with_existing_email_and_other_fields(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'email':'exsisting@email.com',
            'name': 'new name',
            'phone_number': '987654321',
            'post_address': 'new post address'
        }
        
        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'my user with this email already exists.')

    def test_update_user_email_with_valid_email_and_other_fields(self):
        # Arrange
        self.client.force_authenticate(user=self.user)
        data = {
            'email':'new@email.com',
            'name': 'new name',
            'phone_number': '987654321',
            'post_address': 'new post address'
        }

        # Act
        response = self.client.patch(self.url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, data['email'])
        self.assertEqual(self.user.name, data['name'])
        self.assertEqual(self.user.phone_number, data['phone_number'])
        self.assertEqual(self.user.post_address, data['post_address'])
        self.assertEqual(self.user.is_active, False)
