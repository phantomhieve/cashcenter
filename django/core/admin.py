from django.contrib import admin
from .models import FinancialYear, SystemConfig, UserProfile
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.hashers import make_password

@admin.register(FinancialYear)
class FinancialYearAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start_date', 'end_date')
    ordering = ('-start_date',)

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__',)
    
    def has_add_permission(self, request):
        return not SystemConfig.objects.exists()

# User Profile Inline to edit financial year password in User Admin
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Financial Year Settings'
    
    # Optional: Use a form to hash password on save, similar to previous SystemConfig logic
    # But for simplicity, we treat it as a managed field. 
    # If we want hashing, we need a Custom Form here.
    
class UserProfileForm(forms.ModelForm):
    financial_year_password = forms.CharField(
        widget=forms.PasswordInput(render_value=True), 
        help_text="Enter new password to change. Stored as hash if logic implemented, currently implemented as CharField in views.",
        required=False
    )
    class Meta:
        model = UserProfile
        fields = '__all__'
        
    def save(self, commit=True):
        instance = super(UserProfileForm, self).save(commit=False)
        raw_password = self.cleaned_data.get('financial_year_password')
        # Logic from views check_password implies we might want hashing eventually.
        # But currently default 'admin' is plain text. 
        # For now, let's keep it simple: What you type is what is stored (as requested logic implied plain text fallback)
        # OR we implement hashing here for security. 
        # Given "secure" context, hashing is best.
        if raw_password and not raw_password.startswith('pbkdf2_'):
             instance.financial_year_password = make_password(raw_password)
        
        if commit:
            instance.save()
        return instance

# Override inline form if we want hashing (recommended)
UserProfileInline.form = UserProfileForm


# Re-register UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
