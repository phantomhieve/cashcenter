from django.db import models

class StockData(models.Model):
    category = models.CharField(max_length=255)
    company  = models.CharField(max_length=255)
    item     = models.CharField(max_length=255)
    hsn      = models.CharField(max_length=255)
    pcs_mtr  = models.FloatField()
    rate     = models.FloatField()

    def __str__(self):
        return f'{self.hsn} - {self.item}'