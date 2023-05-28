from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Book.models import Book, BookRequest
from Book.serializers import AllBooksSerializer
from rest_framework.test import APIRequestFactory


class RegisterUsersTests(APITestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='existing@user.com',
            password='testpassword',
            name='abc',
            phone_number='123456789'
        )

        self.url = '/auth/register/'

    def tearDown(self) -> None:
        get_user_model().objects.all().delete()

        return super().tearDown()

    def test_register_user_should_return_success(self):
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'name': 'John Doe',
            'phone_number': '123456789'
        }

        # Act
        response = self.client.post(self.url, data, format='json')
        User = get_user_model()
        user = User.objects.get(email='test@example.com')
        user.refresh_from_db()
                
        # Assert    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'Success'})
        self.assertEqual(user.is_active, False)

    def test_register_user_should_return_400_when_user_provides_invalid_email(self):
        # Arrange
        data = {
            'email': 'testexample.com',
            'password': 'testpassword',
            'name': 'John Doe',
            'phone_number': '123456789'
        }

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'Enter a valid email address.')

    def test_register_user_should_return_400_when_user_provides_no_email(self):
        # Arrange
        data = {
            'email': '',
            'password': 'testpassword', 
            'name': 'John Doe',
            'phone_number': '123456789'
        }

        # Act
        response = self.client.post(self.url, data, format='json')


        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'This field may not be blank.')

    def test_register_user_should_return_400_when_user_provides_no_password(self):
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': '',
            'name': 'John Doe',
            'phone_number': '123456789'
        }

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field may not be blank.')

    def test_register_user_should_return_400_when_user_provides_no_name(self):
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'name': '',
            'phone_number': '123456789'
        }

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['name'][0], 'This field may not be blank.')

    def test_register_user_should_return_400_when_user_provides_no_phone_number(self):
        # Arrange
        data = {
            'email': 'test@example.com',
            'password': 'testpassword',
            'name': 'John Doe',
            'phone_number': ''
        }

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['phone_number'][0], 'This field may not be blank.')

    def test_register_user_should_return_400_when_user_provides_existing_email(self):   
        # Arrange
        data = {
            'email':'existing@user.com',
            'password':'testpassword',
            'name':'abc',
            'phone_number':'123456789'
        }

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], 'email exists.')
