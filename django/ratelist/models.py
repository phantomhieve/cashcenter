from djongo import models
from django.contrib.auth.models import User

class RatelistData(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(null=False, max_length=255)
    item     = models.CharField(null=False, max_length=255)
    hsn      = models.CharField(blank=True, null=True, max_length=255)
    company  = models.CharField(blank=True, null=True, max_length=255)
    quantity = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('company', 'item')
        ordering = ['id']

    def __str__(self):
        return f"{self.user} {self.category}/{self.item}"

class RatelistDataHelper(models.Model):
    p_price      = models.FloatField()
    p_date       = models.DateField()
    s_price      = models.FloatField()
    s_date       = models.DateField()
    ratelistdata = models.ForeignKey(to=RatelistData, on_delete=models.CASCADE, related_name='rate')

    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return f"{self.ratelistdata.user}/ {self.id}"
    