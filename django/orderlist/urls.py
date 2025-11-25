from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    OrderListView,
    orderAddView,
    orderDeleteView,
    autocompleteView,
)


urlpatterns = [
    path(
        '',
        login_required(OrderListView.as_view(), login_url='/user/login/'),
        name='order_list'
    ),
    path(
        'add/',
        login_required(orderAddView, login_url='/user/login/'),
        name='order_add'
    ),
    path(
        'add/<int:id>/',
        login_required(orderAddView, login_url='/user/login/'),
        name='order_update'
    ),
    path(
        'delete/<int:id>/',
        login_required(orderDeleteView, login_url='/user/login/'),
        name='order_delete'
    ),
    path(
        'autocomplete/',
        login_required(autocompleteView, login_url='/user/login/'),
        name='order_autocomplete'
    ),
]
