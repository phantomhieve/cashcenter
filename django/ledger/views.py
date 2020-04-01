from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponseRedirect

from .models import LedgerData
from .filters import LedgerDataFilter
from .forms import LedgerDataForm

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



def ledgerAddView(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(LedgerData,id=id)
    if request.method == 'POST':
        form = LedgerDataForm(request.POST ,instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/ledger/')
        return render(
            request,
            '404.html',
        )
    args = {'form': LedgerDataForm(instance=instance)}
    return render(
        request,
        'ledger/add_ledger.html',
        args
    )