from django.urls import path, re_path
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path(
        'login/', 
        LoginView.as_view(template_name='user/login.html'), 
        name='user_login',
    ),
    path(
        'logout/',
        LogoutView.as_view(),
        name='user_logout'
    )
]