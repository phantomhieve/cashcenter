from django.db import models

class FinancialYear(models.Model):
    """Model for Financial Year."""
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.start_date.year}-{self.end_date.year}"

class SystemConfig(models.Model):
    """Global system configuration."""
    financial_year_password = models.CharField(max_length=128, default='admin', help_text="Password required to switch financial year")

    def __str__(self):
        return "System Configuration"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SystemConfig.objects.exists():
            return
        return super(SystemConfig, self).save(*args, **kwargs)

class UserFinancialYear(models.Model):
    """Persist active financial year per user."""
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='financial_year_config')
    financial_year = models.ForeignKey(FinancialYear, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.financial_year}"
