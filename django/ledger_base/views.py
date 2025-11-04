from django.shortcuts import render
from django_filters.views import FilterView
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test

from .models import LedgerDataBase
from .forms import LedgerDataForm
from .backend import makeInstance
from .filters import LedgerDataBaseFilter
from ledger.backend import getUsersFromGroup
from ledger.models import LedgerData


class LedgerBaseListView(FilterView):
    """View for listing and filtering ledger base data."""
    
    model = LedgerDataBase
    template_name = 'ledger_base/list_ledger_base.html'
    filterset_class = LedgerDataBaseFilter
    paginate_by = 3

    def get_context_data(self, **kwargs):
        """Add total bill amount to context."""
        context = super().get_context_data(**kwargs)
        queryset = context['filter'].qs
        
        if queryset and 'bill_ammount' in queryset[0]:
            total = sum(
                ledger.get('bill_ammount', 0) or 0
                for ledger in queryset
            )
            context['total'] = total
        return context


def ledgerAddView(request, id=None):
    """View for adding or updating ledger base data."""
    instance = None
    query = request.GET.copy()
    query.pop('invalid', None)
    
    if id:
        instance = get_object_or_404(
            LedgerDataBase,
            id=id,
            user__in=getUsersFromGroup(request.user)
        )
    elif query.get('l_r_view'):
        instance = get_object_or_404(
            LedgerDataBase,
            l_r_no=query.pop('l_r_view')[0],
            user__in=getUsersFromGroup(request.user)
        )
        return HttpResponseRedirect(
            reverse('ledger_base_update', args=[instance.id]) + f'?{query.urlencode()}'
        )

    if request.method == 'POST':
        form = LedgerDataForm(request.POST, instance=instance)
        
        # Check if user is trying to change l_r_no without staff permission
        if instance and instance.l_r_no != request.POST.get('l_r_no') and not request.user.is_staff:
            return HttpResponseRedirect(reverse('ledger_base_add') + '?invalid=true')
        
        # Check if entry already exists in main ledger
        existing_objects = LedgerData.objects.filter(
            l_r_no=request.POST.get('l_r_no'),
            user__in=getUsersFromGroup(request.user)
        )
        
        if form.is_valid() and not existing_objects.exists():
            ledger = form.save(commit=False)
            ledger.user = request.user
            users = getUsersFromGroup(ledger.user)
            existing_data = LedgerDataBase.objects.filter(
                l_r_no=ledger.l_r_no,
                user__in=users
            )
            
            if not existing_data.exists() or (id and instance.l_r_no == ledger.l_r_no):
                ledger.save()
                if instance:
                    return HttpResponseRedirect(
                        reverse('ledger_base_list') + f'?update={ledger.l_r_no}&{query.urlencode()}'
                    )
                return HttpResponseRedirect(
                    reverse('ledger_base_add') + f'?sucessful={ledger.l_r_no}&{query.urlencode()}'
                )
        return HttpResponseRedirect(reverse('ledger_base_add') + '?invalid=true')
    
    context = {
        'form': LedgerDataForm(instance=instance),
        'instance': instance.id if instance else None
    }
    return render(request, 'ledger_base/add_ledger_base.html', context)


@user_passes_test(lambda u: u.is_staff)
def ledgerDeleteView(request, id=None):
    """View for deleting ledger base data."""
    if id:
        instance = get_object_or_404(LedgerDataBase, id=id)
        l_r_no = instance.l_r_no
        instance.delete()
        return HttpResponseRedirect(reverse('ledger_base_list') + f'?lr-no={l_r_no}')
    return render(request, '404.html')


@user_passes_test(lambda u: u.is_staff)
def approveView(request, id=None):
    """View for approving ledger base entries."""
    if id:
        instance = get_object_or_404(LedgerDataBase, id=id)
        if instance.user in getUsersFromGroup(request.user):
            new_instance = makeInstance(instance, request)
            new_instance.save()
            l_r_no = instance.l_r_no
            instance.delete()
            return HttpResponseRedirect(reverse('ledger_base_list') + f'?approve={l_r_no}')
    return render(request, '404.html')


def autoComplete(request):
    """Provide autocomplete suggestions for ledger base fields."""
    q = request.GET.get('q')
    field = request.GET.get('field')
    
    if q and field:
        users = getUsersFromGroup(request.user)
        lookup = {f'{field}__icontains': q}
        
        data1 = LedgerData.objects.filter(
            **lookup,
            user__in=users
        ).values_list(field, flat=True).distinct()[:10]
        
        data2 = LedgerDataBase.objects.filter(
            **lookup,
            user__in=users
        ).values_list(field, flat=True).distinct()[:10]
        
        # Combine and limit results
        combined_data = list(data1) + list(data2)
        unique_data = list(set(combined_data))[:10]
        
        return JsonResponse(unique_data, safe=False)
    
    return JsonResponse([], safe=False)