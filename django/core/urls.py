from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('switch-year/', views.switch_financial_year, name='switch_financial_year'),
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='core/change_password.html', success_url='/'), name='change_password'),
    path('change-financial-password/', views.change_financial_password, name='change_financial_password'),
]
