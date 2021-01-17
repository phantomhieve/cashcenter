from django.contrib import admin
from .models import LedgerData

class LedgerDataAdmin(admin.ModelAdmin):
    pass

admin.site.register(LedgerData, LedgerDataAdmin)