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
        fields = {
            'l_r_no':['contains'],
            'status':['exact'],
            'delivery':['exact'],
            'reciept':['exact']
        }
    
    l_r_date = django_filters.DateFromToRangeFilter(
        field_name='l_r_date',
        widget=django_filters.widgets.RangeWidget(
            attrs={'type':'date', 'class': 'col-md-2 form-item-half'}
        )
    )
    def filter_by_order(self, queryset, name, value):
        expression = 'id' if value == 'ascending' else '-id'
        return queryset.order_by(expression)