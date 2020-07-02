from django.urls import path, re_path
from django.contrib.auth.views import LogoutView
from .views import LoginView

urlpatterns = [
    path(
        'login/', 
        LoginView.as_view(), 
        name='user_login',
    ),
    path(
        'logout/',
        LogoutView.as_view(),
        name='user_logout'
    )
]