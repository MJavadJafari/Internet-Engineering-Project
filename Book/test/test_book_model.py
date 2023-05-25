from django.contrib.auth import get_user_model
from django.test import TestCase

from Book.models import Book


class BookModelTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        cls.book_data = {
            'name': 'Book Name',
            'description': 'Book Description',
            'translator': 'Book Translator',
            'shabak': 'Book Shabak',
            'publish_year': 'Book Publish Year',
            'is_donated': False,
            'is_received': False,
            'donator': user,
            'author': 'Book Author',
            'number_of_request': 0,
        }

    def test_book_creation_should_create_book(self):
        # Arrange
        book = Book.objects.create(**self.book_data)

        # Act
        book_count = Book.objects.count()

        # Assert
        self.assertEqual(book_count, 1)
        self.assertEqual(book.name, self.book_data['name'])
        self.assertEqual(book.description, self.book_data['description'])
        self.assertEqual(book.translator, self.book_data['translator'])
        self.assertEqual(book.shabak, self.book_data['shabak'])
        self.assertEqual(book.publish_year, self.book_data['publish_year'])
        self.assertEqual(book.is_donated, self.book_data['is_donated'])
        self.assertEqual(book.is_received, self.book_data['is_received'])
        self.assertEqual(book.donator.pk, self.book_data['donator'].pk)
        self.assertEqual(book.author, self.book_data['author'])
        self.assertEqual(book.number_of_request, self.book_data['number_of_request'])


    def test_book_str_representation_should_return_book_name(self):
        # Arrange
        book = Book.objects.create(**self.book_data)

        # Act
        book_str = str(book)

        # Assert
        self.assertEqual(book_str, self.book_data['name'])

