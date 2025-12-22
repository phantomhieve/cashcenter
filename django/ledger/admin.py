from django.contrib import admin
from .models import LedgerData

@admin.register(LedgerData)
class LedgerDataAdmin(admin.ModelAdmin):
    list_display = (
        'l_r_no', 'supplier', 'item', 'no_of_bale',
        'l_r_date', 'status', 'bill_ammount',
    )
    search_fields = ('l_r_no', 'supplier', 'item')
    list_filter = ('status', 'l_r_date')