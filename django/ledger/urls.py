from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import LedgerListView, ledgerAddView

urlpatterns = [
    path(
        '',
        login_required(LedgerListView.as_view(), login_url='/user/login/'),
        name='ledger_list'
    ),
    path(
        'add/',
        login_required(ledgerAddView, login_url='/user/login/'),
        name='ledger_add'
    ),
    path(
        'add/<int:id>/',
        login_required(ledgerAddView, login_url='/user/login/'),
        name='ledger_update'
    )
]