from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Book.models import Book, BookRequest
from Book.serializers import AllBooksSerializer
from rest_framework.test import APIRequestFactory



class AllBooksTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Create test user
        cls.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        cls.second_user = get_user_model().objects.create_user(
            email='second_user@example.com',
            password='testpassword',
            name='Second User',
            phone_number='123456789',
        )


        # Create test books
        cls.book1 = Book.objects.create(
            name='Book 1',
            description='Description 1',
            author='Author 1',
            is_donated=True,
            donator_id=cls.user.pk,
            created_at='2021-01-01'
        )
        cls.book2 = Book.objects.create(
            name='Book 2',
            description='Description 2',
            author='Author 2',
            is_donated=False,
            donator_id=cls.second_user.pk,
            created_at = '2020-01-01'
        )

        cls.url = '/book/all/'


    def setUp(self):
        self.client.force_authenticate(user=self.user)


    def get_serializer_context(self, user):
        request = APIRequestFactory().get(self.url)
        request.user = user
        return {'request': request}


    def test_get_all_books_should_return_all_books(self):
        # Arrange

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        serialized_books = AllBooksSerializer([self.book1, self.book2], many=True, context=self.get_serializer_context(self.user)).data
        # there is no need to check for order of books, so we sort them first
        response_data = sorted(response.data, key=lambda x: x['book_id'])
        serialized_books = sorted(serialized_books, key=lambda x: x['book_id'])
        self.assertEqual(response_data, serialized_books)

    # test if the books are sorted by created_at
    def test_get_all_books_should_return_all_books_sorted_by_created_at(self):
        # Arrange

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        serialized_books = AllBooksSerializer([self.book2, self.book1], many=True, context=self.get_serializer_context(self.user)).data
        self.assertEqual(response.data, serialized_books)


    def test_filter_books_by_donated_status_should_return_filtered_books(self):
        # Arrange
        filters = {'is_donated': True}

        # Act
        response = self.client.get(self.url, filters)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        serialized_books = AllBooksSerializer([self.book1], many=True, context=self.get_serializer_context(self.user)).data
        self.assertEqual(response.data, serialized_books)

    def test_filter_books_by_donator_should_return_filtered_books(self):
        # Arrange
        filters = {'donator': self.user.pk}

        # Act
        response = self.client.get(self.url, filters)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        serialized_books = AllBooksSerializer([self.book1], many=True, context=self.get_serializer_context(self.user)).data
        self.assertEqual(response.data, serialized_books)

    def test_search_books_by_name_should_return_matching_books(self):
        # Arrange
        search_query = 'Book 1'

        # Act
        response = self.client.get(self.url, {'search': search_query})

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        request = APIRequestFactory().get('/book/all/')
        request.user = self.user
        serialized_books = AllBooksSerializer([self.book1], many=True, context=self.get_serializer_context(self.user)).data
        self.assertEqual(response.data, serialized_books)


    def test_not_matching_search_should_return_no_books(self):
        # Arrange
        search_query = 'Book 3'

        # Act
        response = self.client.get(self.url, {'search': search_query})

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)


    def test_no_authentication_should_return_401(self):
        # Arrange
        self.client.force_authenticate(user=None)

        # Act
        response = self.client.get(self.url)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

