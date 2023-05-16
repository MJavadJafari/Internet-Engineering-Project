from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from Book.models import Book


class RegisterBooksTestCase(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

    def setUp(self):
        self.client.force_authenticate(user=self.user)

    def register_book(self, data):
        return self.client.post('/book/register/', data, format='json')

    def test_create_book_should_create_book(self):
        # Arrange
        data = {
            'name': 'Book Name',
            'description': 'Book Description',
            'translator': 'Book Translator',
            'shabak': 'Book Shabak',
            'publish_year': 'Book Publish Year',
            'is_donated': False,
            'is_received': False,
            'donator': self.user.pk,
            'author': 'Book Author',
            'number_of_request': 0,
        }

        # Act
        response = self.register_book(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)
        book = Book.objects.first()
        self.assertEqual(book.name, data['name'])
        self.assertEqual(book.description, data['description'])
        self.assertEqual(book.translator, data['translator'])
        self.assertEqual(book.shabak, data['shabak'])
        self.assertEqual(book.publish_year, data['publish_year'])
        self.assertEqual(book.is_donated, data['is_donated'])
        self.assertEqual(book.is_received, data['is_received'])
        self.assertEqual(book.donator.pk, data['donator'])
        self.assertEqual(book.author, data['author'])
        self.assertEqual(book.number_of_request, data['number_of_request'])


    def test_create_book_without_authentication_should_return_401(self):
        # Arrange
        data = {
            'name': 'Book Name',
            'description': 'Book Description',
            'translator': 'Book Translator',
            'shabak': 'Book Shabak',
            'publish_year': 'Book Publish Year',
            'is_donated': False,
            'is_received': False,
            'donator': self.user.pk,
            'author': 'Book Author',
            'number_of_request': 0,
        }
        self.client.logout()

        # Act
        response = self.register_book(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 0)


    def test_create_book_with_invalid_data_should_return_400(self):
        # Arrange
        data = {}

        # Act
        response = self.register_book(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 0)
