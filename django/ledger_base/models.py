from django.db import models
from django.contrib.auth.models import User


class LedgerDataBase(models.Model):
    """Model for storing base ledger data entries before approval."""
    
    class Meta:
        ordering = ['l_r_date', 'id']
        unique_together = ('user', 'l_r_no')

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    l_r_no = models.CharField(max_length=255)
    l_r_date = models.DateField(blank=True, null=True)
    bale_no = models.CharField(blank=True, null=True, max_length=255)
    supplier = models.CharField(blank=True, null=True, max_length=255)
    location = models.CharField(blank=True, null=True, max_length=255)
    item = models.CharField(blank=True, null=True, max_length=255)
    pcs_mtr = models.FloatField(blank=True, null=True)
    price = models.FloatField(default=0, blank=True)
    weight = models.CharField(blank=True, null=True, max_length=255)
    frieght = models.FloatField(blank=True, null=True)
    transport = models.CharField(blank=True, null=True, max_length=255)
    delivery = models.DateField(blank=True, null=True)
    reciept = models.CharField(blank=True, null=True, max_length=255)
    remark = models.CharField(blank=True, null=True, max_length=255)
    status = models.BooleanField(default=False)
    hsn_code = models.CharField(blank=True, null=True, max_length=255)
    bill_ammount = models.FloatField(blank=True, null=True)
    no_of_bale = models.IntegerField(default=1, blank=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} - {self.l_r_no}'
    
    def calculate_price(self):
        """Calculate price based on bill amount, freight, and pcs_mtr."""
        if self.pcs_mtr and self.bill_ammount and self.frieght:
            self.price = round((self.bill_ammount + self.frieght) / self.pcs_mtr, 2)
    
    def update_status(self):
        """Update status based on receipt and delivery dates."""
        if self.reciept is not None and self.delivery is not None:
            self.status = True
    
    def save(self, *args, **kwargs):
        """Override save to calculate price and update status."""
        self.calculate_price()
        self.update_status()
        super().save(*args, **kwargs)