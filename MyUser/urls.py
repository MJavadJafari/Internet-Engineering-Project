from MyUser.views import UserInfo, RegisterUsers, CustomAuthToken, UpdateUser, ActivateUser, ChangePassword, \
    PasswordReset, ConfirmPasswordReset, BuyVIP
from django.urls import path

urlpatterns = [
    path('register/', RegisterUsers.as_view()),
    path('login/', CustomAuthToken.as_view()),
    path('info/', UserInfo.as_view()),
    path('update/', UpdateUser.as_view()),
    path('activate/<str:token>', ActivateUser.as_view()),
    path('change-password/', ChangePassword.as_view()),
    path('reset-password/', PasswordReset.as_view()),
    path('confirm_password_reset/<str:token>', ConfirmPasswordReset.as_view()),
    path('buy-vip/', BuyVIP.as_view()),
]
