from django.db import models

# Create your models here.

class LedgerData(models.Model):
    l_r_no    = models.CharField(max_length=255)
    l_r_date  = models.DateField(blank=True, null=True)
    bale_no   = models.IntegerField(blank=True, null=True)
    supplier  = models.CharField(blank=True, null=True, max_length=255)
    location  = models.CharField(blank=True, null=True, max_length=255)
    item      = models.CharField(blank=True, null=True, max_length=255)
    pcs_mtr   = models.FloatField(blank=True, null=True)
    price     = models.FloatField(blank=True, null=True)
    weight    = models.CharField(blank=True, null=True, max_length=255)
    frieght   = models.FloatField(blank=True, null=True)
    transport = models.CharField(blank=True, null=True, max_length=255)
    delivery  = models.DateField(blank=True, null=True)
    reciept   = models.CharField(blank=True, null=True, max_length=255)
    remark    = models.CharField(blank=True, null=True, max_length=255)
    status    = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.l_r_no} - {self.supplier}'
    
    def save(self, *args, **kwargs):
        if self.reciept!=None and self.delivery!=None:
            self.status= True
        super(LedgerData, self).save(*args, **kwargs)