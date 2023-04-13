from django.urls import path, re_path

from . import views

urlpatterns = [
    path('request/', views.GoToGatewayView.as_view(), name='request'),
    path('verify/', views.VerifyView.as_view(), name='verify'),
    path('options/', views.VIPOptionsView.as_view(), name='options'),
]
