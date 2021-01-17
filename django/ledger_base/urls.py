from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import(
    LedgerBaseListView, 
    ledgerAddView, 
    ledgerDeleteView,
    approveView,
    autoComplete
)

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
    path(
        'delete/<int:id>/',
        login_required(ledgerDeleteView, login_url='/user/login/'),
        name='ledger_base_delete'
    ),
    path(
        'approve/<int:id>/',
        login_required(approveView, login_url='/user/login/'),
        name='ledger_base_approve'
    ),
     path(
        'autocomplete/',
        login_required(autoComplete, login_url='/user/login/'),
        name='autocomplete_base'
    ),
]