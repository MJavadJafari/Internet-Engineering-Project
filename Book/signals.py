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
        book = instance.book
        request = {
            'id': book.id,
            'summary': book.summary,
        }
        response = requests.post('/insert_book', data=request)

        if response.status_code == 200:
            keywords = response.json()
            book.keywords = keywords
            book.save() 
        else:
            print(f'Request failed with status {response.status_code}: {response.text}')