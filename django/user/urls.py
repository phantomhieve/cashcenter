from django.urls import path, re_path
from django.contrib.auth.views import LoginView

urlpatterns = [
    path(
        '', 
        LoginView.as_view(template_name='user/login.html'), 
        name='login',
    ),
]