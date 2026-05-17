from django.shortcuts import render, redirect, get_object_or_404
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Q

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
        """Add total bill amount to context using database aggregation."""
        context = super().get_context_data(**kwargs)
        filterset = context['filter']
        queryset = filterset.qs
        
        # Check if 'bill_ammount' is in the selected columns
        selected_columns = self.request.GET.getlist('columns')
        context['selected_columns'] = selected_columns  # Pass to template
        
        if 'bill_ammount' in selected_columns:
            # Use database aggregation instead of Python sum for better performance
            # Check if column filter is applied (which returns values queryset)
            if self.request.GET.get('columns'):
                # Column filter was applied, so queryset is a values queryset
                # Create a new queryset without column filter for aggregation
                # This ensures we get all filtered records but calculate total correctly
                get_params = self.request.GET.copy()
                get_params.pop('columns', None)  # Remove column filter
                base_filterset = self.filterset_class(
                    get_params,
                    queryset=self.model.objects.filter(
                        user=self.request.user,
                        financial_year=getattr(self.request, 'financial_year', None)
                    ),
                    request=self.request
                )
                base_qs = base_filterset.qs
                # Check if base_qs is a regular queryset (not values queryset)
                # A values queryset has '_fields' attribute, regular queryset doesn't
                if hasattr(base_qs, 'model') and not hasattr(base_qs, '_fields'):
                    # Regular queryset - use aggregation
                    total = base_qs.aggregate(total=Sum('bill_ammount'))['total'] or 0
                else:
                    # Values queryset - calculate from the filtered queryset
                    # But we need to get bill_ammount from the original queryset
                    # Since queryset is already filtered, we can sum from it
                    total = sum(
                        ledger.get('bill_ammount', 0) or 0
                        for ledger in queryset
                    )
                context['total'] = total
            elif queryset and hasattr(queryset, 'model'):
                # No column filter, use aggregation directly on model queryset
                total = queryset.aggregate(total=Sum('bill_ammount'))['total'] or 0
                context['total'] = total
        return context

@user_passes_test(lambda u: u.is_staff)
def ledgerAddView(request, id=None):
    """View for adding or updating ledger data."""
    instance = None
    query = request.GET.copy()
    
    if id:
        instance = get_object_or_404(
            LedgerData.objects.select_related('user'),
            id=id,
            user=request.user
        )
    elif query.get('l_r_view'):
        instance = get_object_or_404(
            LedgerData.objects.select_related('user'),
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
            ledger.financial_year = getattr(request, 'financial_year', None)
            # Use exists() instead of len() for better performance
            existing_data = LedgerData.objects.filter(
                l_r_no=ledger.l_r_no,
                user=ledger.user,
                financial_year=ledger.financial_year
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
        queryset = (
            LedgerData.objects.filter(
                **lookup,
                user__in=users,
                financial_year=getattr(request, 'financial_year', None)
            )
            .order_by(field)
            .values_list(field, flat=True)
        )

        unique_results = []
        seen = set()

        for value in queryset:
            if value is None:
                continue
            # Normalize to string for comparison but keep original text for display
            normalized = str(value).strip().lower()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            unique_results.append(str(value).strip())
            if len(unique_results) >= 10:
                break

        return JsonResponse(unique_results, safe=False)
    
    return JsonResponse([], safe=False)