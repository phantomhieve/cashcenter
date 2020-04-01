from django.urls import path
from .views import ledgerView

urlpatterns = [
    path(
        '',
        ledgerView,
        name='ledger_list'
    )
]