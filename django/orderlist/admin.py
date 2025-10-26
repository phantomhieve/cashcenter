from django.contrib import admin
from .models import Order, Fulfillment


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
	list_display = (
		'order_number', 'company_name', 'item', 'num_parcels',
		'order_date', 'fulfilment_status', 'order_price',
	)
	search_fields = ('order_number', 'company_name', 'item')
	list_filter = ('fulfilment_status', 'order_date')


@admin.register(Fulfillment)
class FulfillmentAdmin(admin.ModelAdmin):
	list_display = ('order', 'date', 'quantity')
	list_filter = ('date',)
	search_fields = ('order__order_number',)
