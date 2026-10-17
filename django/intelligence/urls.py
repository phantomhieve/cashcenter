from django.urls import path
from . import views

app_name = 'intelligence'

urlpatterns = [
    path('auth/', views.auth_gate, name='auth_gate'),
    path('api/verify-password/', views.api_verify_password, name='api_verify_password'),
    path('api/translate/', views.api_translate, name='api_translate'),
    path('lock/', views.lock_dashboard, name='lock_dashboard'),
    path('', views.dashboard, name='dashboard'),
    path('run/', views.run_analysis, name='run_analysis'),
    path('run/<int:run_id>/', views.run_detail, name='run_detail'),
    path('run/<int:run_id>/feedback/', views.submit_feedback, name='submit_feedback'),
]
