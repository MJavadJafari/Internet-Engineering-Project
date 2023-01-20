from django.contrib import admin
from django.urls import path, include

from Book.views import BookInfo, RegisterBooks, ActiveBooks, MyBooks

urlpatterns = [
    path('<int:pk>/', BookInfo.as_view()),
    path('active/', ActiveBooks.as_view()),
    path('register/', RegisterBooks.as_view()),
    path('mybooks/', MyBooks.as_view()),

]
