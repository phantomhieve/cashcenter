from django.shortcuts import render
from django_filters.views import FilterView
from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test

from .models import LedgerDataBase
from .forms import LedgerDataForm
from .backend import makeInstance
from .filters import LedgerDataBaseFilter
from ledger.backend import getUsersFromGroup
from ledger.models import LedgerData

class LedgerBaseListView(FilterView):
    model = LedgerDataBase
    template_name = 'ledger_base/list_ledger_base.html'
    filterset_class = LedgerDataBaseFilter
    paginate_by =3

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
    query = request.GET.copy()
    query.pop('invalid', None)
    if id:
        instance = get_object_or_404(
            LedgerDataBase,
            id=id,
            user__in = getUsersFromGroup(request.user)
        )
    elif query.get('l_r_view', False):
        instance = get_object_or_404(
            LedgerDataBase, 
            l_r_no=query.pop('l_r_view')[0],
            user__in = getUsersFromGroup(request.user)
        )
        return HttpResponseRedirect(f'/ledger_base/add/{instance.id}/?{query.urlencode()}')

    if request.method == 'POST':
        form = LedgerDataForm(request.POST, instance=instance)
        
        if instance and instance.l_r_no!=request.POST['l_r_no'] and (not self.request.user.is_staff):
            return HttpResponseRedirect('/ledger_base/add/?invalid=true')
        
        objects = LedgerData.objects.filter(l_r_no=request.POST['l_r_no'], user__in=getUsersFromGroup(request.user))
        if form.is_valid() and len(objects)==0:
            ledger = form.save(commit=False)
            ledger.user = request.user
            users = getUsersFromGroup(ledger.user)
            data  = LedgerDataBase.objects.filter(
                l_r_no=ledger.l_r_no,
                user__in=users
            )
            if (not len(data)) or (id and instance.l_r_no==ledger.l_r_no):
                ledger.save()
                if instance:
                    return HttpResponseRedirect(f'/ledger_base/?update={ledger.l_r_no}&{query.urlencode()}')
                return HttpResponseRedirect(f'/ledger_base/add/?sucessful={ledger.l_r_no}&{query.urlencode()}')
        return HttpResponseRedirect('/ledger_base/add/?invalid=true')
    args = {
        'form': LedgerDataForm(instance=instance),
        'instance': instance.id if instance else None
    }
    return render(
        request,
        'ledger_base/add_ledger_base.html',
        args
    )

@user_passes_test(lambda u: u.is_staff)
def ledgerDeleteView(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(LedgerDataBase, id=id)
        instance.delete()
        return HttpResponseRedirect(f'/ledger_base?lr-no={instance.l_r_no}')
    return render(
        request,
        '404.html',
    )
@user_passes_test(lambda u: u.is_staff)
def approveView(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(LedgerDataBase, id=id)
        if instance.user in getUsersFromGroup(request.user):
            new_instance = makeInstance(instance, request)
            new_instance.save()
            instance.delete()
            return HttpResponseRedirect(f'/ledger_base?approve={instance.l_r_no}')
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
        data1 = LedgerData.objects.filter(**kwargs, user__in=users)\
            .values_list(field, flat=True).distinct().order_by()[:10]
        
        data2 = LedgerDataBase.objects.filter(**kwargs, user__in=users)\
            .values_list(field, flat=True).distinct().order_by()[:10]
        
        print('----------------------------')
        print(data1)
        print(data2)
        print('----------------------------')
        data = list(data1)+ list(data2)
        json = list(data[:10])
        return JsonResponse(json, safe=False)
    else:
        HttpResponse("No cookies")