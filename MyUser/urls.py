from MyUser.views import UserInfo, RegisterUsers, CustomAuthToken, UpdateUser, ActivateUser
from django.urls import path

urlpatterns = [
    path('register/', RegisterUsers.as_view()),
    path('login/', CustomAuthToken.as_view()),
    path('info/', UserInfo.as_view()),
    path('update/', UpdateUser.as_view()),
    path('activate/<str:token>', ActivateUser.as_view()),
]
