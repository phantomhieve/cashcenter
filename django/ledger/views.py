from django.shortcuts import render, redirect
from django_filters.views import FilterView
from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from .models import LedgerData
from .filters import LedgerDataFilter, DEFAULT
from .forms import LedgerDataForm

class LedgerListView(FilterView):
    model = LedgerData
    template_name = 'ledger/list_ledger.html'
    filterset_class  = LedgerDataFilter
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['object_list'] and  type(context['object_list'][0])!=dict:
            context['object_list'] = context['object_list'].values(*DEFAULT)
        return context

def ledgerAddView(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(LedgerData, id=id)
    if request.method == 'POST':
        form = LedgerDataForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/ledger/')
        return render(
            request,
            '404.html',
        )
    args = {
        'form': LedgerDataForm(instance=instance),
        'instance': instance.id if instance else None
    }
    return render(
        request,
        'ledger/add_ledger.html',
        args
    )

def ledgerDeleteView(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(LedgerData, id=id)
        instance.delete()
        return HttpResponseRedirect(f'/ledger?lr-no={instance.l_r_no}')
    return render(
        request,
        '404.html',
    )

def autoComplete(request):
    if request.GET.get('q') and request.GET['field']:
        field = request.GET['field']
        q = request.GET['q']
        kwargs = {
            '{0}__{1}'.format(field, 'startswith'): q,
        }
        data = LedgerData.objects.filter(**kwargs).values_list(field, flat=True)
        json = list(set(data))
        return JsonResponse(json, safe=False)
    else:
        HttpResponse("No cookies")