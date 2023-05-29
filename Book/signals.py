from django.conf import settings
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
from Book.models import BookRequest, Book
import requests
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BookRequest)
def book_request_created(sender, instance, created, **kwargs):
    if created:
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_request_created_signal: book = {instance.book} user = {instance.user}")
        book = instance.book
        book.number_of_request = book.number_of_request + 1
        book.save()
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_request_create_signal: book = {book} number_of_request = {book.number_of_request}")


@receiver(post_delete, sender=BookRequest)
def book_request_deleted(sender, instance, **kwargs):
    logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_request_deleted_signal: book = {instance.book} user = {instance.user}")
    book = instance.book
    book.number_of_request = max(book.number_of_request - 1, 0)
    book.save()
    logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_request_delete_signal: book = {book} number_of_request = {book.number_of_request}")


@receiver(post_save, sender=Book)
def book_created(sender, instance, created, **kwargs):
    if created:
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_created_signal: book = {instance}")
        request = {
            'id': instance.book_id,
            'summary': str(instance.description),
        }

        if settings.USE_FLASK_SERVER:
            try:
                logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_created_signal: book = {instance}, trying to send request to flask server")
                response = requests.post(settings.FLASK_SERVER_ADDRESS + '/insert_book', data=request)
                if response.status_code == 200:
                    logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_created_signal: book = {instance}, request was successful, book inserted to flask server")
                    keywords = response.json()
                    instance.keywords = keywords
                else:
                    if settings.DEBUG:
                        print(f'Request failed with status {response.status_code}: {response.text}')
                        instance.keywords = instance.description.split(' ')[:5]
                    else:
                        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_created_signal: book = {instance}, request failed with status {response.status_code}: {response.text}")
                        instance.keywords = []
            except:
                logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_created_signal: book = {instance}, request failed")
                if settings.DEBUG:
                    print(f'Request failed')
                    instance.keywords = instance.description.split(' ')[:5]
                else:
                    instance.keywords = []
        logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_created_signal: book = {instance}, keywords = {instance.keywords}")
        instance.save()



@receiver(post_delete, sender=Book)
def book_deleted(sender, instance, **kwargs):
    logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_deleted_signal: book = {instance}")
    request = {
        'id': instance.book_id,
    }

    if settings.USE_FLASK_SERVER:
        try:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_deleted_signal: book = {instance}, trying to send request to flask server")
            response = requests.post(settings.FLASK_SERVER_ADDRESS + '/delete_book', data=request)
            if response.status_code == 200:
                logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_deleted_signal: book = {instance}, request was successful, book deleted from flask server")
            else:
                logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_deleted_signal: book = {instance}, request failed with status {response.status_code}: {response.text}")
        except:
            logger.info("[%s] [%s] [%s]", timezone.now(), logging.getLevelName(logging.INFO), f"book_deleted_signal: book = {instance}, request failed")
