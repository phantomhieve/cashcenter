from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import LedgerBaseListView, ledgerAddView

urlpatterns = [
    path(
        '',
        login_required(LedgerBaseListView.as_view(), login_url='/user/login/'),
        name='ledger_base_list'
    ),
    path(
        'add/',
        login_required(ledgerAddView, login_url='/user/login/'),
        name='ledger_base_add'
    ),
    path(
        'add/<int:id>/',
        login_required(ledgerAddView, login_url='/user/login/'),
        name='ledger_base_update'
    ),
]