from django.db import models


class Book(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    book_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=60, blank=False)
    description = models.TextField(max_length=250, blank=False)
    picture = models.ImageField(upload_to='book/', blank=True)
    is_donated = models.BooleanField(default=False)
    is_received = models.BooleanField(default=False)
    donator = models.ForeignKey('MyUser.MyUser', on_delete=models.CASCADE, blank=True, related_name='donator')
    author = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return self.name


class BookRequest(models.Model):
    class Meta:
        unique_together = [['user', 'book']]

    user = models.ForeignKey('MyUser.MyUser', on_delete=models.CASCADE, related_name='user')
    book = models.ForeignKey('Book.Book', on_delete=models.CASCADE, related_name='book')
    is_pending = models.BooleanField(default=True)
    is_accepted = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
