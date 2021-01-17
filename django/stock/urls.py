from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    StockListView, 
    stockAddView, 
    stockDeleteView, 
    autoComplete
)

urlpatterns = [
    path(
        '',
        login_required(StockListView.as_view(), login_url='/user/login/'),
        name='stock_list'
    ),
    path(
        'add/',
        login_required(stockAddView, login_url='/user/login/'),
        name='stock_add'
    ),
    path(
        'add/<int:id>/',
        login_required(stockAddView, login_url='/user/login/'),
        name='stock_update'
    ),
    path(
        'delete/<int:id>/',
        login_required(stockDeleteView, login_url='/user/login/'),
        name='stock_delete'
    ),
    path(
        'autocomplete/',
        login_required(autoComplete, login_url='/user/login/'),
        name='stock_autocomplete'
    ),
]