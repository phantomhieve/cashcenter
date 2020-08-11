from django.shortcuts import render
from django.views.generic import ListView
from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse


from .models import LedgerDataBase
from .forms import LedgerDataForm
from ledger.backend import getUsersFromGroup
from ledger.models import LedgerData

class LedgerBaseListView(ListView):
    model = LedgerDataBase
    template_name = 'ledger_base/list_ledger_base.html'
    paginate_by=25


def ledgerAddView(request, id=None):
    instance = None
    query = request.GET.copy()
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
