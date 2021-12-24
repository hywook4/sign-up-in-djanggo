from django.urls import path
from . import views

urlpatterns = [
    path('', views.UserAPIView.as_view()),
    path('auth', views.AuthAPIView.as_view())
]