from django.apps import AppConfig
import requests
from django.conf import settings


class BookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Book'

    def ready(self):
        import Book.signals as signals
        from Book.models import Book

        try:
            req = {}
            for item in Book.objects.all():
                req[item.book_id] = str(item.description)

            response = requests.post(settings.FLASK_SERVER_ADDRESS + '/init_model', json=req)
        except Exception as e:
            print(e)

