from django.shortcuts import render
from django.views.generic import ListView

from .models import LedgerDataBase

class LedgerBaseListView(ListView):
    model = LedgerDataBase
    template_name = 'ledger_base/list_ledger_base.html'
    paginate_by=25
