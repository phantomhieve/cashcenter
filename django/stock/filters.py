import django_filters
from .models import StockData

class StockDataFilter(django_filters.FilterSet):

    class Meta:

        model  = StockData
        fields = {
            'item': ['contains'],
            'hsn': ['contains'],
            'category': ['contains']
        }
    
    @property
    def qs(self):
        parent = super(StockDataFilter, self).qs
        return parent.filter(user = self.request.user)\
            .order_by('id')