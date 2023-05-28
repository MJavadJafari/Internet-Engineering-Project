from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from Book.models import Book
from Book.serializers import BookSerializer


class BookInfoTestCase(APITestCase):
    user = None

    def setUp(self):        
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        self.book = Book.objects.create(
            name='Book Name',
            description='Book Description',
            translator='Book Translator',
            shabak='Book Shabak',
            publish_year='Book Publish Year',
            is_donated=False,
            is_received=False,
            donator=self.user,
            author='Book Author',
            number_of_request=0,
        )

        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        Book.objects.all().delete()
        get_user_model().objects.all().delete()

        return super().tearDown()

    def get_book_info(self, book_id):
        return self.client.get(f'/book/{book_id}/')

    def test_retrieve_book_info_should_return_book_info(self):
        # Arrange

        # Act
        response = self.get_book_info(self.book.book_id)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = BookSerializer(instance=self.book).data
        self.assertEqual(response.data, expected_data)
        self.assertEqual(response.data['name'], self.book.name)
        self.assertEqual(response.data['description'], self.book.description)
        self.assertEqual(response.data['translator'], self.book.translator)
        self.assertEqual(response.data['shabak'], self.book.shabak)
        self.assertEqual(response.data['publish_year'], self.book.publish_year)
        self.assertEqual(response.data['is_donated'], self.book.is_donated)
        self.assertEqual(response.data['is_received'], self.book.is_received)
        self.assertEqual(response.data['donator'], self.book.donator.pk)
        self.assertEqual(response.data['author'], self.book.author)
        self.assertEqual(response.data['number_of_request'], self.book.number_of_request)



    def test_retrieve_book_info_without_authentication_should_return_401(self):
        # Arrange
        self.client.logout()

        # Act
        response = self.get_book_info(self.book.book_id)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_retrieve_nonexistent_book_info_should_return_404(self):
        # Arrange
        nonexistent_book_id = 999

        # Act
        response = self.get_book_info(nonexistent_book_id)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Add more assertions based on your specific requirements
