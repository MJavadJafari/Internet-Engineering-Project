from django.contrib import admin
from django.urls import path, include

from Book.views import BookInfo, RegisterBooks

urlpatterns = [
    path('<int:pk>/', BookInfo.as_view()),
    path('register/', RegisterBooks.as_view()),
]
