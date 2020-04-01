from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import LedgerListView

urlpatterns = [
    path(
        '',
        login_required(LedgerListView.as_view(), login_url='/login/'),
        name='ledger_list'
    )
]