from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    RatelistAddView, 
    ratelistDeleteView,
    RatelistListView
)

urlpatterns = [
    path(
        '',
        login_required(RatelistListView.as_view(), login_url='/user/login/'),
        name='ratelist_list'
    ),
    path(
        'add/',
        login_required(RatelistAddView.as_view(), login_url='/user/login/'),
        name='ratelist_add'
    ),
    path(
        'add/<int:id>/',
        login_required(RatelistAddView.as_view(), login_url='/user/login/'),
        name='ratelist_update'
    ),
    path(
        'delete/<int:id>/',
        login_required(ratelistDeleteView, login_url='/user/login/'),
        name='ratelist_delete'
    ),
]