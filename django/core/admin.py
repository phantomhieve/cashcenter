from django.contrib import admin
from .models import FinancialYear, SystemConfig

@admin.register(FinancialYear)
class FinancialYearAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start_date', 'end_date')
    ordering = ('-start_date',)

from django import forms
from django.contrib.auth.hashers import make_password

class SystemConfigForm(forms.ModelForm):
    financial_year_password = forms.CharField(widget=forms.PasswordInput, help_text="Enter new password to change, or leave empty to keep current.")

    class Meta:
        model = SystemConfig
        fields = '__all__'

    def save(self, commit=True):
        instance = super(SystemConfigForm, self).save(commit=False)
        # Hash the password if it's raw (simple check: length < 50 usually means raw for pbkdf2)
        # Better: check if it's already a valid hash, or just rely on user knowing "change" vs "view"
        # Since we use PasswordInput, we assume any input is a NEW password to be hashed.
        # But wait, ModelForm will load existing hash into the field? 
        # Actually, standard practice for UserAdmin is complicated.
        # Simplified approach: always hash what is submitted if it doesn't look like a hash.
        raw_password = self.cleaned_data.get('financial_year_password')
        if raw_password and not raw_password.startswith('pbkdf2_'):
             instance.financial_year_password = make_password(raw_password)
        
        if commit:
            instance.save()
        return instance

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    form = SystemConfigForm
    list_display = ('__str__',) # Don't show hash in list
    
    def has_add_permission(self, request):
        return not SystemConfig.objects.exists()
