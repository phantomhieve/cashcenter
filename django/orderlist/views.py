from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django_filters.views import FilterView
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from ledger.backend import getUsersFromGroup

from .models import Order
from .filters import OrderFilter
from .forms import OrderForm, FulfillmentFormSet


class OrderListView(FilterView):
    """View for listing and filtering orders."""
    
    model = Order
    template_name = 'orderlist/list_order.html'
    filterset_class = OrderFilter
    paginate_by = 25

    def get(self, *args, **kwargs):
        """Check if user is staff before allowing access."""
        if not self.request.user.is_staff:
            return redirect('/')
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Filter queryset - default to pending if no filters applied."""
        queryset = super().get_queryset().select_related('user')
        
        # Check if any filters are applied
        has_filters = any([
            self.request.GET.get('order_number__icontains'),
            self.request.GET.get('company_name__icontains'),
            self.request.GET.get('item__icontains'),
            self.request.GET.get('status'),
            self.request.GET.get('mode'),
            self.request.GET.get('agent_name__icontains'),
            self.request.GET.get('order_date'),
        ])
        
        # Default to pending status if no filters are applied
        if not has_filters:
            queryset = queryset.filter(fulfilment_status=Order.FulfilmentStatus.PENDING)
        
        return queryset.order_by('-order_date')


@user_passes_test(lambda u: u.is_staff)
def orderAddView(request, id=None):
    """View for adding or updating orders."""
    instance = None
    if id:
        instance = get_object_or_404(
            Order.objects.select_related('user').prefetch_related('fulfillments'),
            id=id,
            user=request.user
        )
    
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=instance)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            # Save first to ensure PK exists before binding inline formset
            order.save()
            formset = FulfillmentFormSet(request.POST, instance=order)
            if formset.is_valid():
                formset.save()
                if instance:
                    return HttpResponseRedirect(
                        reverse('order_update', args=[order.id]) + f'?update={order.order_number}'
                    )
                return HttpResponseRedirect(
                    reverse('order_add') + f'?sucessful={order.order_number}'
                )
            # If formset invalid, fall through to render with errors
            return render(
                request,
                'orderlist/add_order.html',
                {'form': form, 'formset': formset, 'instance': order.id}
            )
        # Form invalid: render with an empty inline formset
        formset = FulfillmentFormSet(instance=instance) if instance else FulfillmentFormSet(instance=Order())
        return render(
            request,
            'orderlist/add_order.html',
            {'form': form, 'formset': formset, 'instance': instance.id if instance else None}
        )
    else:
        form = OrderForm(instance=instance)
        formset = FulfillmentFormSet(instance=instance) if instance else FulfillmentFormSet(instance=Order())
    return render(
        request,
        'orderlist/add_order.html',
        {'form': form, 'formset': formset, 'instance': instance.id if instance else None}
    )


@user_passes_test(lambda u: u.is_staff)
def orderDeleteView(request, id=None):
    """View for deleting orders."""
    if id:
        instance = get_object_or_404(Order, id=id)
        order_number = instance.order_number
        instance.delete()
        return HttpResponseRedirect(reverse('order_list') + f'?order-no={order_number}')
    return render(request, '404.html')

@user_passes_test(lambda u: u.is_staff)
def autocompleteView(request):
    """View for autocomplete suggestions."""
    if 'field' not in request.GET or 'q' not in request.GET:
        return JsonResponse([], safe=False)

    field = request.GET['field']
    query = request.GET['q']
    
    allowed_fields = ['company_name', 'item', 'agent_name', 'transport', 'order_number']
    if field not in allowed_fields:
        return JsonResponse([], safe=False)

    # Filter for values containing the query and belonging to the user's group
    users = getUsersFromGroup(request.user)
    results = Order.objects.filter(
        **{f"{field}__icontains": query},
        user__in=users
    ).order_by(field).values_list(field, flat=True)

    unique_results = []
    seen = set()

    for value in results:
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
