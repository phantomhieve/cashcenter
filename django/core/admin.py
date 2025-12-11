from django.contrib import admin
from .models import FinancialYear

@admin.register(FinancialYear)
class FinancialYearAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'start_date', 'end_date')
    ordering = ('-start_date',)
