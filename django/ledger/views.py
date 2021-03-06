from django.shortcuts import render, redirect
from django_filters.views import FilterView
from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test

from .models import LedgerData
from .filters import LedgerDataFilter, DEFAULT
from .forms import LedgerDataForm
from .backend import getUsersFromGroup

class LedgerListView(FilterView):
    model = LedgerData
    template_name = 'ledger/list_ledger.html'
    filterset_class  = LedgerDataFilter
    paginate_by=25

    def get(self, *args, **kwargs):
        if not self.request.user.is_staff:
            return redirect('/')
        return super(LedgerListView, self).get(*args, **kwargs)

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

@user_passes_test(lambda u: u.is_staff)
def ledgerAddView(request, id=None):
    instance = None
    query = request.GET.copy()
    if id:
        instance = get_object_or_404(
            LedgerData, 
            id=id,
            user=request.user
        )
    elif query.get('l_r_view', False):
        instance = get_object_or_404(
            LedgerData, 
            l_r_no=query.pop('l_r_view')[0],
            user=request.user
        )
        return HttpResponseRedirect(f'/ledger/add/{instance.id}/?{query.urlencode()}')

    if request.method == 'POST':
        form = LedgerDataForm(request.POST, instance=instance)
        if form.is_valid():
            ledger = form.save(commit=False)
            ledger.user = request.user
            data  = LedgerData.objects.filter(
                l_r_no=ledger.l_r_no,
                user=ledger.user
            )
            if (not len(data)) or (id and instance.l_r_no==ledger.l_r_no):
                ledger.save()
                if instance:
                    return HttpResponseRedirect(f'/ledger/?update={ledger.l_r_no}&{query.urlencode()}')
                return HttpResponseRedirect(f'/ledger/add/?sucessful={ledger.l_r_no}&{query.urlencode()}')
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

@user_passes_test(lambda u: u.is_staff)
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
            .values_list(field, flat=True).distinct().order_by()[:10]
        json = list(data)
        return JsonResponse(json, safe=False)
    else:
        HttpResponse("No cookies")