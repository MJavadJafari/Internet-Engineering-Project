from django.contrib import admin
from django.urls import path, include

from Book.views import BookInfo, RegisterBooks, AllBooks, AddRequest, Requests_to_me

urlpatterns = [
    path('<int:pk>/', BookInfo.as_view()),
    path('all/', AllBooks.as_view()),
    path('register/', RegisterBooks.as_view()),
    path('request/register/', AddRequest.as_view()),
    path('request/requeststome/', Requests_to_me.as_view()),
    # path('mybooks/', MyBooks.as_view()),
]
