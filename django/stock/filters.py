import django_filters
from .models import StockData


class StockDataFilter(django_filters.FilterSet):
    """FilterSet for filtering StockData."""
    
    class Meta:
        model = StockData
        fields = {
            'item': ['contains'],
            'hsn': ['contains'],
            'category': ['contains']
        }
    
    @property
    def qs(self):
        """Filter queryset by user and order by id."""
        queryset = super().qs
        queryset = queryset.filter(user=self.request.user)
        if getattr(self.request, 'financial_year', None):
            queryset = queryset.filter(financial_year=self.request.financial_year)
        return queryset.order_by('id')