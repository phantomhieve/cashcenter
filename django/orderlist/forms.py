from django import forms
from django.forms import inlineformset_factory
from .models import Order, Fulfillment


class OrderForm(forms.ModelForm):
	class Meta:
		model = Order
		fields = [
			'order_number', 'company_name', 'item', 'num_parcels',
			'order_date', 'fulfilment_status', 'order_price', 'mode', 'agent_name', 'remark'
		]
		widgets = {
			'remark': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
		}

	def clean(self):
		cleaned_data = super().clean()
		mode = cleaned_data.get('mode')
		agent_name = cleaned_data.get('agent_name')

		# If mode is 'agent', agent_name is required
		if mode == 'agent' and not agent_name:
			self.add_error('agent_name', 'Agent name is required when mode is Agent.')

		# If mode is not 'agent', clear agent_name
		if mode != 'agent':
			cleaned_data['agent_name'] = None

		return cleaned_data


FulfillmentFormSet = inlineformset_factory(
	parent_model=Order,
	model=Fulfillment,
	fields=('date', 'quantity'),
	extra=1,
	can_delete=True
)
