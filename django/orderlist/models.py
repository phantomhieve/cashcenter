from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db.models import Sum


class Order(models.Model):
    """Model for storing order information."""
    
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
    financial_year = models.ForeignKey(
        'core.FinancialYear',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
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
    agent_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Required only when mode is 'Agent'"
    )
    transport = models.CharField(max_length=255, blank=True, null=True)
    remark = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order_date', 'id']
        indexes = [
            models.Index(fields=['order_date', '-id']),
            models.Index(fields=['fulfilment_status', 'order_date']),
            models.Index(fields=['user', 'order_date']),
        ]

    def __str__(self) -> str:
        return f"{self.user} - {self.order_number}"

    @property
    def fulfilled_parcels(self) -> int:
        """Calculate total fulfilled parcels."""
        # Use aggregation instead of fetching all fulfillments
        return self.fulfillments.aggregate(total=Sum('quantity'))['total'] or 0

    def update_status_from_fulfillments(self) -> None:
        """Update order status based on fulfillment data."""
        if self.fulfilment_status == self.FulfilmentStatus.CANCELLED:
            return
        if self.fulfilled_parcels >= (self.num_parcels or 0):
            self.fulfilment_status = self.FulfilmentStatus.COMPLETED
        else:
            self.fulfilment_status = self.FulfilmentStatus.PENDING

    def save(self, *args, **kwargs):
        """Override save to update status from fulfillments."""
        # Ensure we have a primary key before accessing related fulfillments
        is_new = self.pk is None
        # Save first to obtain PK if new
        super().save(*args, **kwargs)
        # Recompute status after initial save or when fields change
        previous_status = self.fulfilment_status
        # Only try to compute from fulfillments when PK exists
        self.update_status_from_fulfillments()
        if self.fulfilment_status != previous_status:
            super().save(update_fields=['fulfilment_status'])


class Fulfillment(models.Model):
    """Model for storing order fulfillment information."""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='fulfillments'
    )
    date = models.DateField()
    quantity = models.IntegerField()
    bill_no = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['date', 'id']

    def __str__(self) -> str:
        return f"{self.order.order_number} - {self.date} - {self.quantity}"

    def save(self, *args, **kwargs):
        """Override save to update parent order status."""
        super().save(*args, **kwargs)
        # After saving a fulfillment, update the parent order status
        self.order.update_status_from_fulfillments()
        self.order.save(update_fields=['fulfilment_status'])
