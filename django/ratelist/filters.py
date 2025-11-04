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
        return queryset.filter(user=self.request.user)