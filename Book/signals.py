from django.conf import settings
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
from Book.models import BookRequest, Book
import requests


@receiver(post_save, sender=BookRequest)
def book_request_created(sender, instance, created, **kwargs):
    if created:
        book = instance.book
        book.number_of_request = book.number_of_request + 1
        book.save()


@receiver(post_delete, sender=BookRequest)
def book_request_deleted(sender, instance, **kwargs):
    book = instance.book
    book.number_of_request = max(book.number_of_request - 1, 0)
    book.save()


@receiver(post_save, sender=Book)
def book_created(sender, instance, created, **kwargs):
    if created:
        request = {
            'id': instance.book_id,
            'summary': str(instance.description),
        }

        if settings.USE_FLASK_SERVER:
            try:
                response = requests.post(settings.FLASK_SERVER_ADDRESS + '/insert_book', data=request)
                if response.status_code == 200:
                    keywords = response.json()
                    instance.keywords = keywords
                else:
                    if settings.DEBUG:
                        print(f'Request failed with status {response.status_code}: {response.text}')
                        instance.keywords = instance.description.split(' ')[:5]
                    else:
                        instance.keywords = []
            except:
                if settings.DEBUG:
                    print(f'Request failed')
                    instance.keywords = instance.description.split(' ')[:5]
                else:
                    instance.keywords = []

        instance.save()



@receiver(post_delete, sender=Book)
def book_deleted(sender, instance, **kwargs):
    request = {
        'id': instance.book_id,
    }

    if settings.USE_FLASK_SERVER:
        try:
            response = requests.post(settings.FLASK_SERVER_ADDRESS + '/delete_book', data=request)
            if response.status_code == 200:
                print('Book deleted successfully')
            else:
                print(f'Request failed with status {response.status_code}: {response.text}')
        except:
            print(f'Request failed')
