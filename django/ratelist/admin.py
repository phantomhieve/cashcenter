from django.contrib import admin
from .models import RatelistData, RatelistDataHelper

class RatelistDataHelperInline(admin.TabularInline):
    model = RatelistDataHelper

class RatelistDataAdmin(admin.ModelAdmin):
    inlines = [
        RatelistDataHelperInline,
    ]
admin.site.register(RatelistData, RatelistDataAdmin)
