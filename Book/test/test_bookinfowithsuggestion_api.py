# # test for book info with suggestion
# class BookInfoWithSuggestion(APIView):
#     permission_classes = [
#         permissions.IsAuthenticated
#     ]
#
#     def get(self, request, pk):
#         try:
#             book = Book.objects.get(book_id=pk)
#         except:
#             return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)
#
#         req = {
#             'id': book.book_id,
#         }
#
#         similar_books = Book.objects.all().exclude(book_id=book.book_id).order_by('?')[:5]
#
#         response = {
#             "book": AllBooksSerializer(book, context={'request': request}).data,
#             "similar_books": AllBooksSerializer(similar_books, many=True, context={'request': request}).data,
#         }
#         return Response(response, status=HTTP_200_OK)

from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Book.models import Book, BookRequest
from Book.serializers import AllBooksSerializer

class BookInfoWithSuggestionTests(APITestCase):

    def setUp(self):
        # Create test user
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        # Create test book
        self.book1 = Book.objects.create(
            name='Book 1',
            description='Description 1',
            author='Author 1',
            is_donated=False,
            donator_id=self.user.pk,
        )
        self.book2 = Book.objects.create(
            name='Book 2',
            description='Description 2',
            author='Author 2',
            is_donated=False,
            donator_id=self.user.pk,
        )
        self.book3 = Book.objects.create(
            name='Book 3',
            description='Description 3',
            author='Author 3',
            is_donated=False,
            donator_id=self.user.pk,
        )
        self.book4 = Book.objects.create(
            name='Book 4',
            description='Description 4',
            author='Author 4',
            is_donated=False,
            donator_id=self.user.pk,
        )
        self.book5 = Book.objects.create(
            name='Book 5',
            description='Description 5',
            author='Author 5',
            is_donated=True,
            donator_id=self.user.pk,
        )

        self.client.force_authenticate(user=self.user)

        self.url = '/book/info-suggestion/'

    def make_request(self, book_id):
        return self.client.get(self.url + str(book_id) + '/')


    def test_book_info_with_suggestion_should_return_200(self):
        # Arrange
        book_id = self.book1.pk

        # Act
        response = self.make_request(book_id)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_book_info_with_suggestion_should_return_400_if_book_does_not_exist(self):
        # Arrange
        book_id = 999

        # Act
        response = self.make_request(book_id)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'Invalid request'})

    def test_book_info_with_suggestion_should_not_return_donated_book(self):
        # Arrange
        book_id = self.book1.pk

        # Act
        response = self.make_request(book_id)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for book in response.data['similar_books']:
            self.assertEqual(book['is_donated'], False)

    def test_book_info_with_suggestion_should_not_return_same_book(self):
        # Arrange
        book_id = self.book1.pk

        # Act
        response = self.make_request(book_id)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for book in response.data['similar_books']:
            self.assertNotEqual(book['book_id'], book_id)


    def test_book_info_with_suggestion_should_return_5_books(self):
        # Arrange
        book_id = self.book1.pk
        # add more books
        for i in range(5):
            Book.objects.create(
                name='Book ' + str(i + 6),
                description='Description ' + str(i + 6),
                author='Author ' + str(i + 6),
                is_donated=False,
                donator_id=self.user.pk,
            )

        # Act
        response = self.make_request(book_id)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['similar_books']), 5)

    def test_unauthenticated_user_should_not_access(self):
        # Arrange
        book_id = self.book1.pk
        self.client.force_authenticate(user=None)

        # Act
        response = self.make_request(book_id)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
