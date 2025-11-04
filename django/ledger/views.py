from django.shortcuts import render, redirect, get_object_or_404
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test

from .models import LedgerData
from .filters import LedgerDataFilter
from .forms import LedgerDataForm
from .backend import getUsersFromGroup


class LedgerListView(FilterView):
    """View for listing and filtering ledger data."""
    
    model = LedgerData
    template_name = 'ledger/list_ledger.html'
    filterset_class = LedgerDataFilter
    paginate_by = 25

    def get(self, *args, **kwargs):
        """Check if user is staff before allowing access."""
        if not self.request.user.is_staff:
            return redirect('/')
        return super().get(*args, **kwargs)

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

@user_passes_test(lambda u: u.is_staff)
def ledgerAddView(request, id=None):
    """View for adding or updating ledger data."""
    instance = None
    query = request.GET.copy()
    
    if id:
        instance = get_object_or_404(
            LedgerData,
            id=id,
            user=request.user
        )
    elif query.get('l_r_view'):
        instance = get_object_or_404(
            LedgerData,
            l_r_no=query.pop('l_r_view')[0],
            user=request.user
        )
        return HttpResponseRedirect(
            reverse('ledger_update', args=[instance.id]) + f'?{query.urlencode()}'
        )

    if request.method == 'POST':
        form = LedgerDataForm(request.POST, instance=instance)
        if form.is_valid():
            ledger = form.save(commit=False)
            ledger.user = request.user
            existing_data = LedgerData.objects.filter(
                l_r_no=ledger.l_r_no,
                user=ledger.user
            )
            
            if not existing_data.exists() or (id and instance.l_r_no == ledger.l_r_no):
                ledger.save()
                if instance:
                    return HttpResponseRedirect(
                        reverse('ledger_list') + f'?update={ledger.l_r_no}&{query.urlencode()}'
                    )
                return HttpResponseRedirect(
                    reverse('ledger_add') + f'?sucessful={ledger.l_r_no}&{query.urlencode()}'
                )
        return HttpResponseRedirect(reverse('ledger_add') + '?invalid=true')
    
    context = {
        'form': LedgerDataForm(instance=instance),
        'instance': instance.id if instance else None
    }
    return render(request, 'ledger/add_ledger.html', context)

@user_passes_test(lambda u: u.is_staff)
def ledgerDeleteView(request, id=None):
    """View for deleting ledger data."""
    if id:
        instance = get_object_or_404(LedgerData, id=id)
        l_r_no = instance.l_r_no
        instance.delete()
        return HttpResponseRedirect(reverse('ledger_list') + f'?lr-no={l_r_no}')
    return render(request, '404.html')


def autoComplete(request):
    """Provide autocomplete suggestions for ledger fields."""
    q = request.GET.get('q')
    field = request.GET.get('field')
    
    if q and field:
        users = getUsersFromGroup(request.user)
        lookup = {f'{field}__icontains': q}
        data = LedgerData.objects.filter(
            **lookup,
            user__in=users
        ).values_list(field, flat=True).distinct()[:10]
        
        return JsonResponse(list(data), safe=False)
    
    return JsonResponse([], safe=False)