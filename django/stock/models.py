from djongo import models
from django.contrib.auth.models import User

class StockData(models.Model):
    user     = models.OneToOneField(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=255)
    company  = models.CharField(max_length=255)
    item     = models.CharField(max_length=255)
    hsn      = models.CharField(max_length=255)
    pcs_mtr  = models.FloatField()
    rate     = models.FloatField()
    
    class Meta:
        ordering = ('hsn',)

    def __str__(self):
        return f'{self.hsn} - {self.item}'