from django.contrib import admin
from django.urls import path, include

from Book.views import BookInfo, RegisterBooks, AllBooks, AddRequest, My_requests, ConfirmDonate, \
    DeleteBook, DeleteRequest, ReportRequest, ReceiveBook, BookInfoWithSuggestion

urlpatterns = [
    path('<int:pk>/', BookInfo.as_view()),
    path('all/', AllBooks.as_view()),
    path('register/', RegisterBooks.as_view()),
    path('request/register/', AddRequest.as_view()),
    path('request/myrequests/', My_requests.as_view()),
    path('confirmdonate/', ConfirmDonate.as_view()),
    path('delete/', DeleteBook.as_view()),
    path('request/delete/', DeleteRequest.as_view()),
    path('request/report/', ReportRequest.as_view()),
    path('request/receivebook/', ReceiveBook.as_view()),
    path('info-suggestion/<int:pk>/', BookInfoWithSuggestion.as_view()),
]
