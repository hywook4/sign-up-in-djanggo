from django.urls import path
from . import views

urlpatterns = [
    path('all', views.UserAPIView.as_view({'get': 'get_all'})),
    path('', views.UserAPIView.as_view({'post': 'sign_up_user'})),
    path('password', views.UserAPIView.as_view({'put': 'change_password'})),
    path('my-info/', views.UserAPIView.as_view({'get':'get_my_info'})),
    path('auth', views.AuthAPIView.as_view())
]