from django.db import models
from django.contrib.auth.models import User

class LedgerData(models.Model):

    class Meta:
        ordering = ['l_r_date', 'id']
        unique_together = ('user', 'l_r_no')

    user         = models.ForeignKey(User, on_delete=models.CASCADE)
    l_r_no       = models.CharField(max_length=255)
    l_r_date     = models.DateField(blank=True, null=True)
    bale_no      = models.CharField(blank=True, null=True, max_length=255)
    supplier     = models.CharField(blank=True, null=True, max_length=255)
    location     = models.CharField(blank=True, null=True, max_length=255)
    item         = models.CharField(blank=True, null=True, max_length=255)
    pcs_mtr      = models.FloatField(blank=True, null=True)
    price        = models.FloatField(default=0, blank=True)
    weight       = models.CharField(blank=True, null=True, max_length=255)
    frieght      = models.FloatField(blank=True, null=True)
    transport    = models.CharField(blank=True, null=True, max_length=255)
    delivery     = models.DateField(blank=True, null=True)
    reciept      = models.CharField(blank=True, null=True, max_length=255)
    remark       = models.CharField(blank=True, null=True, max_length=255)
    status       = models.BooleanField(default=False)
    hsn_code     = models.CharField(blank=True, null=True, max_length=255)
    bill_ammount = models.FloatField(blank=True, null=True)
    no_of_bale   = models.IntegerField(default=1, blank=True)

    def __str__(self):
        return f'{self.user} - {self.l_r_no}'
    
    def save(self, *args, **kwargs):
        if self.pcs_mtr and self.bill_ammount and self.frieght:
            self.price = (self.bill_ammount+self.frieght)/self.pcs_mtr
            self.price = round(self.price, 2)
            
        if self.reciept!=None and self.delivery!=None:
            self.status= True
        super(LedgerData, self).save(*args, **kwargs)