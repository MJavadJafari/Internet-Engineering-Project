from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Book.models import BookRequest, Book
from Book.serializers import BookRequestSerializer

class AddRequestTests(APITestCase):
    
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        self.book1 = Book.objects.create(
            name='Book 1',
            description='Description 1',
            author='Author 1',
            is_donated=False,
            donator_id=self.user.pk,
        )

        self.user.refresh_from_db()
        self.book1.refresh_from_db()
        self.client.force_authenticate(user=self.user)

    def make_request(self, data):
        url = '/book/request/register/'
        response = self.client.post(url, data, format='json')
        return response

    def test_add_request_without_enough_rooyesh_should_return_error(self):
        # Arrange
        self.user.rooyesh = 0
        self.user.save()

        data = {
            'book': 1,
        }

        # Act
        response = self.make_request(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Not enough rooyesh')
        self.assertEqual(BookRequest.objects.count(), 0)

    def test_add_request_should_create_request(self):
        # Arrange
        data = {
            'book': 1,
        }

        # Act
        response = self.make_request(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookRequest.objects.count(), 1)
        self.assertEqual(BookRequest.objects.first().user, self.user)
        self.assertEqual(BookRequest.objects.first().book_id, 1)

    def test_add_request_with_existing_request_should_return_existing_request(self):
        # Arrange
        existing_request = BookRequest.objects.create(
            user=self.user,
            book=self.book1,
        )

        data = {
            'book': 1,
        }

        # Act
        response = self.make_request(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BookRequest.objects.count(), 1)
        self.assertEqual(BookRequest.objects.first().pk, existing_request.pk)
        serialized_response = BookRequestSerializer(existing_request).data
        self.assertEqual(serialized_response, response.data)
        self.assertEqual(BookRequest.objects.first().pk, existing_request.pk)

    def test_add_request_with_donated_book_should_return_error(self):
        # Arrange
        self.book1.is_donated = True
        self.book1.save()

        data = {
            'book': 1,
        }

        # Act
        response = self.make_request(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Book is already donated')
        self.assertEqual(BookRequest.objects.count(), 0)

    # test unauthenticated user
    def test_add_request_without_authentication_should_return_error(self):
        # Arrange
        self.client.force_authenticate(user=None)

        data = {
            'book': 1,
        }

        # Act
        response = self.make_request(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Authentication credentials were not provided.')
        self.assertEqual(BookRequest.objects.count(), 0)

    def test_add_request_with_invalid_book_id_should_return_error(self):
        # Arrange
        data = {
            'book': 999,
        }

        # Act
        response = self.make_request(data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(BookRequest.objects.count(), 0)