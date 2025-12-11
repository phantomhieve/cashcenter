import django_filters
from .models import RatelistData


class RatelistDataFilter(django_filters.FilterSet):
    """FilterSet for filtering RatelistData."""
    
    class Meta:
        model = RatelistData
        fields = {
            'category': ['icontains'],
            'company': ['icontains'],
            'item': ['icontains'],
            'hsn': ['icontains']
        }

    @property
    def qs(self):
        """Filter queryset by user."""
        queryset = super().qs
        queryset = queryset.filter(user=self.request.user)
        if getattr(self.request, 'financial_year', None):
            queryset = queryset.filter(financial_year=self.request.financial_year)
        return queryset