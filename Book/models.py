from django.db import models


class Book(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    book_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=60, blank=False)
    description = models.TextField(max_length=250, blank=False)
    # picture = models.ImageField(upload_to='book/', blank=True)
    picture = models.CharField(max_length=200, blank=True)
    translator = models.CharField(max_length=50, blank=True)
    shabak = models.CharField(max_length=50, blank=True)
    publish_year = models.CharField(max_length=20, blank=True)
    is_donated = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    donator = models.ForeignKey('MyUser.MyUser', on_delete=models.CASCADE, blank=True, related_name='donator')
    author = models.CharField(max_length=60, blank=True)


    def __str__(self):
        return self.name


class BookRequest(models.Model):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'

    constraints = [
        models.UniqueConstraint(
            fields=['user', 'book'], name='unique_migration'
        )
    ]
    user = models.ForeignKey('MyUser.MyUser', on_delete=models.CASCADE, related_name='requests_per_user', blank=True)
    book = models.ForeignKey('Book.Book', on_delete=models.CASCADE, related_name='requests_for_book')
    status = models.CharField(max_length=3, default=PENDING)
    is_reported = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
