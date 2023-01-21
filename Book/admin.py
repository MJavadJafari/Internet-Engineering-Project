from django.contrib import admin
import Book.models

admin.site.register(Book.models.Book)
admin.site.register(Book.models.BookRequest)
