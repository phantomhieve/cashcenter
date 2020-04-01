import django_filters
from .models import LedgerData

class LedgerDataFilter(django_filters.FilterSet):

    CHOICES = (
        ('ascending', 'Ascending'),
        ('descending', 'Descending')
    )

    ordering = django_filters.ChoiceFilter(
        label  = 'Ordering',
        choices = CHOICES,
        method = 'filter_by_order' 
    )

    class Meta:
        model = LedgerData
        fields = ('l_r_date', 'status', 'delivery', 'reciept')
    
    def filter_by_order(self, queryset, name, value):
        expression = 'id' if value == 'ascending' else '-id'
        return queryset.order_by(expression)