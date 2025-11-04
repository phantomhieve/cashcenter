from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from django_filters.views import FilterView
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.urls import reverse

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
        queryset = super().get_queryset()
        
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
        instance = get_object_or_404(Order, id=id, user=request.user)
    
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
