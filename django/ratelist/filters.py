import django_filters
from .models import RatelistData

class RatelistDataFilter(django_filters.FilterSet):
    
    class Meta:
        model = RatelistData
        fields = {
            'category': ['icontains'],
            'company':['icontains'],
            'item': ['icontains'],
            'hsn': ['icontains']
        }
    

    # Overriding Method
    @property
    def qs(self):
        queryset = super(RatelistDataFilter, self).qs
        return queryset.filter(user=self.request.user)