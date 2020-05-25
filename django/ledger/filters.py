import django_filters
from .models import LedgerData

DEFAULT = (
    'l_r_no',
    'l_r_date',
    'item',
    'transport',
    'status',
)

class LedgerDataFilter(django_filters.FilterSet):

    CHOICES = (
        ('l_r_no', 'L R No'),
        ('l_r_date', 'L R Date'),
        ('bale_no', 'Bale No'),
        ('supplier', 'Supplier'),
        ('location', 'Location'),
        ('item ', 'Item'),
        ('pcs_mtr', 'PCS/MTR'),
        ('price', 'Price'),
        ('weight', 'Weight'),
        ('frieght', 'Frieght'),
        ('transport', 'Transport'),
        ('delivery', 'Delivery date'),
        ('reciept', 'Reciept'),
        ('remark', 'Remark'),
        ('status', 'Status'),
        ('hsn_code','HSN Code'),
        ('bill_ammount', 'Bill Ammount'),
        ('l_r_count', 'L R Count')
    )

    class Meta:
        model = LedgerData
        fields = {
            'l_r_no':['contains'],
            'status':['exact'],
            'delivery':['exact'],
            'reciept':['exact'],
            'bale_no':['contains'],
            'item':['contains']
        }

    columns = django_filters.MultipleChoiceFilter(
        label  = 'Columns',
        choices = CHOICES,
        method = 'filter_by_column',
        initial= DEFAULT
    )

    def filter_by_column(self, queryset, name, value):
        return queryset.values(*value)


    l_r_date = django_filters.DateFromToRangeFilter(
        field_name='l_r_date',
        widget=django_filters.widgets.RangeWidget(
            attrs={'type':'date', 'class': 'col-md-2 form-item-half'}
        )
    )