from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import StockListView

urlpatterns = [
    path(
        '',
        login_required(StockListView.as_view(), login_url='/user/login/'),
        name='stock_list'
    ),
]