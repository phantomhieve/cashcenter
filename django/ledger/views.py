from django.shortcuts import render, redirect
from django_filters.views import FilterView
from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from .models import LedgerData
from .filters import LedgerDataFilter, DEFAULT
from .forms import LedgerDataForm
from .backend import getUsersFromGroup

class LedgerListView(FilterView):
    model = LedgerData
    template_name = 'ledger/list_ledger.html'
    filterset_class  = LedgerDataFilter
    paginate_by=25

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if len(context['filter'].qs) and \
            'bill_ammount' in context['filter'].qs[0]:
            total = sum([
                ledger['bill_ammount'] if ledger['bill_ammount'] else 0
                for ledger in context['filter'].qs
            ])
            context["total"] = total
        return context

def ledgerAddView(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(LedgerData, id=id)
    if request.method == 'POST':
        form = LedgerDataForm(request.POST, instance=instance)
        if form.is_valid():
            ledger = form.save(commit=False)
            ledger.user = request.user
            users = getUsersFromGroup(ledger.user)
            data  = LedgerData.objects.filter(
                l_r_no=ledger.l_r_no,
                user__in=users
            )
            if (not len(data)) or (id and instance.l_r_no==ledger.l_r_no):
                ledger.save()
                return HttpResponseRedirect(f'/ledger?sucessful={ledger.l_r_no}')
        return HttpResponseRedirect('/ledger/add/?invalid=true')
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
        users = getUsersFromGroup(request.user)
        kwargs = {
            '{0}__{1}'.format(field, 'icontains'): q,
        }
        data = LedgerData.objects.filter(**kwargs, user__in=users)\
            .values_list(field, flat=True)
        json = list(set(data))[:10]
        return JsonResponse(json, safe=False)
    else:
        HttpResponse("No cookies")