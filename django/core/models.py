from django.db import models

class FinancialYear(models.Model):
    """Model for Financial Year."""
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.start_date.year}-{self.end_date.year}"
