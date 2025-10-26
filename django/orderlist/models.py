from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
	class FulfilmentStatus(models.TextChoices):
		COMPLETED = 'completed', _('Completed')
		CANCELLED = 'cancelled', _('Cancelled')
		PENDING = 'pending', _('Pending')

	class Mode(models.TextChoices):
		PHONE = 'phone', _('Phone')
		WHATSAPP = 'whatsapp', _('WhatsApp')
		PHYSICAL = 'physical', _('Physical')
		AGENT = 'agent', _('Agent')

	user = models.ForeignKey(User, on_delete=models.CASCADE)
	order_number = models.CharField(max_length=255)
	company_name = models.CharField(max_length=255)
	item = models.CharField(max_length=255)
	num_parcels = models.IntegerField()
	order_date = models.DateField()
	fulfilment_status = models.CharField(
		max_length=16,
		choices=FulfilmentStatus.choices,
		default=FulfilmentStatus.PENDING,
	)
	order_price = models.FloatField(default=0)
	mode = models.CharField(
		max_length=16,
		choices=Mode.choices,
		default=Mode.PHONE,
	)
	agent_name = models.CharField(max_length=255, blank=True, null=True, help_text="Required only when mode is 'Agent'")
	remark = models.TextField(blank=True, null=True)

	class Meta:
		ordering = ['order_date', 'id']
		unique_together = ('user', 'order_number')

	def __str__(self) -> str:
		return f"{self.user} - {self.order_number}"

	@property
	def fulfilled_parcels(self) -> int:
		return sum(
			f.quantity for f in self.fulfillments.all()
		)

	def update_status_from_fulfillments(self) -> None:
		if self.fulfilment_status == self.FulfilmentStatus.CANCELLED:
			return
		if self.fulfilled_parcels >= (self.num_parcels or 0):
			self.fulfilment_status = self.FulfilmentStatus.COMPLETED
		else:
			self.fulfilment_status = self.FulfilmentStatus.PENDING

	def save(self, *args, **kwargs):
		# Ensure we have a primary key before accessing related fulfillments
		is_new = self.pk is None
		# Save first to obtain PK if new
		super().save(*args, **kwargs)
		# Recompute status after initial save or when fields change
		previous_status = self.fulfilment_status
		# Only try to compute from fulfillments when PK exists
		self.update_status_from_fulfillments()
		if self.fulfilment_status != previous_status:
			super(Order, self).save(update_fields=['fulfilment_status'])


class Fulfillment(models.Model):
	order = models.ForeignKey(
		Order,
		on_delete=models.CASCADE,
		related_name='fulfillments'
	)
	date = models.DateField()
	quantity = models.IntegerField()

	class Meta:
		ordering = ['date', 'id']

	def __str__(self) -> str:
		return f"{self.order.order_number} - {self.date} - {self.quantity}"

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		# After saving a fulfillment, update the parent order status
		self.order.update_status_from_fulfillments()
		self.order.save(update_fields=['fulfilment_status'])
