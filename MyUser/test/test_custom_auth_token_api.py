from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

class CustomAuthTokenTests(APITestCase):

    def setUp(self):
        # Create test user
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        self.url = '/auth/login/'

    def tearDown(self) -> None:
        get_user_model().objects.all().delete()

        return super().tearDown()

    def test_login_should_return_token(self):
        # Arrange
        data = {
            'username': self.user.email,
            'password': 'testpassword',
        }
    
        # Act
        response = self.client.post(self.url, data, format='json')
    
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], self.user.auth_token.key)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['name'], self.user.name)
        self.assertEqual(response.data['phone_number'], self.user.phone_number)
        self.assertEqual(response.data['user_id'], self.user.user_id)
        self.assertEqual(response.data['rooyesh'], self.user.rooyesh)
        

    def test_login_should_return_400_when_user_provides_invalid_password(self):
       # Arrange
        data = {
            'username': self.user.email,
            'password': 'wrongpassword'
        }
        
        # Act
        response = self.client.post(self.url, data, format='json')
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        print(response.data)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to log in with provided credentials.')
    
    def test_login_should_return_400_when_user_provides_invalid_email(self):
        # Arrange
        data = {
            'username': 'wrongemail@example',
            'password': 'testpassword'
        }

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to log in with provided credentials.')

    def test_login_should_return_400_when_user_provides_no_email(self):
        # Arrange
        data = {
            'password': 'testpassword'
        }

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'][0], 'This field is required.')

    def test_login_should_return_400_when_user_provides_no_password(self):
        # Arrange
        data = {
            'username': self.user.email,
        }

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['password'][0], 'This field is required.')

    def test_login_should_return_400_when_user_provides_no_credentials(self):
        # Arrange
        data = {}

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['username'][0], 'This field is required.')
        self.assertEqual(response.data['password'][0], 'This field is required.')

    def test_login_should_return_200_when_user_is_vip_and_vip_end_date_is_passed(self):
        # Arrange
        data = {
            'username': self.user.email,
            'password': 'testpassword'
        }
        self.user.is_vip = True
        self.user.vip_end_date = '2020-01-01'
        self.user.vip_end_time = '00:00:00'
        self.user.refresh_from_db()

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['token'], self.user.auth_token.key)
        self.assertEqual(self.user.is_vip, False)
        self.assertEqual(response.data['email'], self.user.email)
        self.assertEqual(response.data['name'], self.user.name)
        self.assertEqual(response.data['phone_number'], self.user.phone_number)
        self.assertEqual(response.data['user_id'], self.user.user_id)
        self.assertEqual(response.data['rooyesh'], self.user.rooyesh)

    def test_login_should_return_400_when_user_is_not_active(self):
        # Arrange
        data = {
            'username': self.user.email,
            'password': self.user.password
        }
        self.user.is_active = False
        self.user.refresh_from_db()

        # Act
        response = self.client.post(self.url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Unable to log in with provided credentials.')
