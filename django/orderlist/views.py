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
	model = Order
	template_name = 'orderlist/list_order.html'
	filterset_class = OrderFilter
	paginate_by = 25

	def get(self, *args, **kwargs):
		if not self.request.user.is_staff:
			return redirect('/')
		return super(OrderListView, self).get(*args, **kwargs)

	def get_queryset(self):
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
	instance = None
	if id:
		instance = get_object_or_404(Order, id=id, user=request.user)
	if request.method == 'POST':
		form = OrderForm(request.POST, instance=instance)
		if form.is_valid():
			order = form.save(commit=False)
			order.user = request.user
			# prevent duplicate order_number per user
			exists = Order.objects.filter(order_number=order.order_number, user=order.user)
			if (not len(exists)) or (instance and instance.order_number == order.order_number):
				# Save first to ensure PK exists before binding inline formset
				order.save()
				formset = FulfillmentFormSet(request.POST, instance=order)
				if formset.is_valid():
					formset.save()
					if instance:
						return HttpResponseRedirect(f'/orderlist/add/{order.id}/?update={order.order_number}')
					return HttpResponseRedirect(f'/orderlist/add/?sucessful={order.order_number}')
				# If formset invalid, fall through to render with errors
				return render(
					request,
					'orderlist/add_order.html',
					{'form': form, 'formset': formset, 'instance': order.id}
				)
			# Duplicate/invalid business rule
			return HttpResponseRedirect('/orderlist/add/?invalid=true')
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
	if id:
		instance = get_object_or_404(Order, id=id)
		code = instance.order_number
		instance.delete()
		return HttpResponseRedirect(f'/orderlist?order-no={code}')
	return render(request, '404.html')
