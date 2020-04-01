from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import LedgerData
from .filters import LedgerDataFilter

class LedgerListView(ListView):
    model = LedgerData
    template_name = 'ledger/list_ledger.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = LedgerDataFilter(
            self.request.GET, 
            queryset=self.get_queryset()
        )
        return context
    




'''def ledgerView(request):
    args = {}
    return render(
        request, 
        'ledger/view_ledger.html',
        args
    )
'''
