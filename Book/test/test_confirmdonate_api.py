# # test for confirm donate api
#
# class ConfirmDonate(APIView):
#     permission_classes = [
#         permissions.IsAuthenticated,
#     ]
#
#     def post(self, request):
#         print(request.data)
#         try:
#             book = Book.objects.get(is_donated=False, donator=self.request.user, book_id=request.data['book'])
#         except:
#             return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)
#
#         all_requests = BookRequest.objects.filter(book=book)
#         registered_users = MyUser.objects.filter(user_id__in=all_requests.values_list('user'))
#         if len(registered_users) == 0:
#             return Response({"No one signed up yet"}, status=HTTP_400_BAD_REQUEST)
#
#         registered_users = list(registered_users)
#         random_weights = [x.credit * 1.1 if x.is_user_vip() else x.credit for x in registered_users]
#         chosen_user = random.choices(registered_users, weights=random_weights, k=1)[0]
#
#         # set request status
#         for req in all_requests:
#             if req.user == chosen_user:
#                 req.status = BookRequest.APPROVED
#             else:
#                 req.status = BookRequest.REJECTED
#
#             req.save()
#
#         # set book donated
#         book.is_donated = True
#         book.save()
#
#         return Response({"phone_number": chosen_user.phone_number,
#                          "name": chosen_user.name,
#                          "post_address": chosen_user.post_address}, status=HTTP_200_OK)

from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from Book.models import Book, BookRequest
from Book.serializers import AllBooksSerializer
from rest_framework.test import APIRequestFactory


class TestConfirmDonate(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='testpassword',
            name='John Doe',
            phone_number='123456789'
        )

        self.second_user = get_user_model().objects.create_user(
            email='second_user@example.com',
            password='testpassword',
            name='Second User',
            phone_number='123456789',
        )

        # Create test books
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
            donator_id=self.second_user.pk,
        )
        self.book3 = Book.objects.create(
            name='Book 3',
            description='Description 3',
            author='Author 3',
            is_donated=True,
            donator_id=self.user.pk,
        )

        self.url = '/book/confirmdonate/'

    def test_confirm_donate_should_return_400_if_book_is_donated(self):
        # Arrange
        bookRequest = BookRequest.objects.create(user_id=self.user.pk, book_id=self.book3.pk, status=BookRequest.PENDING)

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'book': self.book3.pk}, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'Invalid request'})

    def test_confirm_donate_should_return_400_if_book_is_not_donated_by_user(self):
        # Arrange
        bookRequest = BookRequest.objects.create(user_id=self.user.pk, book_id=self.book2.pk, status=BookRequest.PENDING)

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'book': self.book2.pk}, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'Invalid request'})

    def test_confirm_donate_on_book_with_no_request_should_return_400(self):
        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'book': self.book1.pk}, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'No one signed up yet'})


    def test_confirm_donate_on_book_with_one_request_should_return_200(self):
        # Arrange
        book_request = BookRequest.objects.create(user_id=self.user.pk, book_id=self.book1.pk, status=BookRequest.PENDING)

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'book': self.book1.pk}, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'phone_number': self.user.phone_number,
                                         'name': self.user.name,
                                         'post_address': self.user.post_address})
        self.assertEqual(Book.objects.get(pk=self.book1.pk).is_donated, True)
        self.assertEqual(BookRequest.objects.get(pk=book_request.pk).status, BookRequest.APPROVED)


    def test_confirm_donate_on_book_with_multiple_request_should_return_200(self):
        # Arrange
        book_request1 = BookRequest.objects.create(user_id=self.user.pk, book_id=self.book1.pk, status=BookRequest.PENDING)
        book_request2 = BookRequest.objects.create(user_id=self.second_user.pk, book_id=self.book1.pk, status=BookRequest.PENDING)

        # Act
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'book': self.book1.pk}, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Book.objects.get(pk=self.book1.pk).is_donated, True)
        # exactly one request should be approved, the other should be rejected, we don't know which one
        book_request_results = [BookRequest.objects.get(pk=book_request1.pk).status, BookRequest.objects.get(pk=book_request2.pk).status]
        self.assertEqual(book_request_results.count(BookRequest.APPROVED), 1)
        self.assertEqual(book_request_results.count(BookRequest.REJECTED), len(book_request_results) - 1)


    def test_not_authenticated_user_should_return_401(self):
        # Act
        response = self.client.post(self.url, {'book': self.book1.pk}, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
