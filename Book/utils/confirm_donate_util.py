from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from Book.user_selection_strategy.user_selection import UserSelectionStrategy
from Book.models import BookRequest
from Book.models import Book
from django.utils import timezone
import logging
logger = logging.getLogger(__name__)


class ConfirmDonateUtil:
    def __init__(self, strategy: UserSelectionStrategy):
        self.user_selection_strategy = strategy

    def confirm_donate(self, request: Request):
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), "ConfirmDonate.post")
        try:
            book = Book.objects.get(is_donated=False, donator=request.user, book_id=request.data['book'])
        except:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO),
                        "ConfirmDonate.post: book not found, response = 400")
            return Response({"Invalid request"}, status=HTTP_400_BAD_REQUEST)

        all_requests = BookRequest.objects.filter(book=book)
        registered_users = [x.user for x in all_requests if x.status == BookRequest.PENDING]
        if len(registered_users) == 0:
            return Response({"No one signed up yet"}, status=HTTP_400_BAD_REQUEST)

        print("registered_users: ", registered_users)
        chosen_user = self.user_selection_strategy.select_user(registered_users)

        # set request status
        for req in all_requests:
            if req.user == chosen_user:
                req.status = BookRequest.APPROVED
            else:
                req.status = BookRequest.REJECTED

            req.save()
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO),
                        f"ConfirmDonate.post: request with user {req.user} and book {req.book} set to {req.status}")

        # set book donated
        book.is_donated = True
        book.save()

        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO),
                    f"ConfirmDonate.post: book {book} set to donated")

        return Response({"phone_number": chosen_user.phone_number,
                         "name": chosen_user.name,
                         "post_address": chosen_user.post_address}, status=HTTP_200_OK)
