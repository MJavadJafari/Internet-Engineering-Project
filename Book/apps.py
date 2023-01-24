from django.apps import AppConfig



class BookConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Book'

    def ready(self):
        try:
            from Recommender.Recommender import SingletonRecommender
            import os
            from Book.models import Book
            if os.environ.get('RUN_MAIN'):
                rec = SingletonRecommender()
                dic = {}
                for item in Book.objects.all():
                    dic[item.book_id] = item.description
                rec.init_model(dic)
        except Exception as e:
            print(e)

