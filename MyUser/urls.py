from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from MyUser.views import UserInfo, RegisterUsers

urlpatterns = [
    path('register/', RegisterUsers.as_view()),
    path('token/', obtain_auth_token),
    path('info/', UserInfo.as_view()),
]
