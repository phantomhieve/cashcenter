from django.urls import path
from . import views

urlpatterns = [
    path('switch-year/', views.switch_financial_year, name='switch_financial_year'),
]
