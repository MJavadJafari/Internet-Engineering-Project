from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
from Book.models import BookRequest


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
