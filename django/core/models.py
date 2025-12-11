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
    # financial_year_password removed in favor of per-user UserProfile

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

class UserProfile(models.Model):
    """Extended user profile for additional settings."""
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    financial_year_password = models.CharField(max_length=128, default='admin', help_text="Password required to switch financial year")

    def __str__(self):
        return f"Profile for {self.user.username}"

# Signals to auto-create UserProfile
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure profile exists even if not created (e.g. legacy users during save)
    # But mainly to save modifications if needed in future
    if not hasattr(instance, 'profile'):
         UserProfile.objects.create(user=instance)
    instance.profile.save()
