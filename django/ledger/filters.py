import django_filters

from .models import LedgerData
from .backend import getUsersFromGroup

DEFAULT = (
    'l_r_no',
    'no_of_bale',
    'bale_no',
    'item',
    'transport',
    'status',
    'id'
)

class LedgerDataFilter(django_filters.FilterSet):
    def __init__(self, data=None, queryset=None, request=None, prefix=None):
        self.values = DEFAULT
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)

    CHOICES = (
        ('l_r_no', 'L R No'),
        ('no_of_bale', 'No Of Bale'),
        ('l_r_date', 'L R Date'),
        ('bale_no', 'Bale No'),
        ('supplier', 'Supplier'),
        ('location', 'Location'),
        ('item', 'Item'),
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
    )

    def filter_by_column(self, queryset, name, value):
        value.append('id')
        self.values = value
        users = getUsersFromGroup(self.request.user)
        return queryset.filter(user__in=users).values(*values)

    l_r_date = django_filters.DateFromToRangeFilter(
        field_name='l_r_date',
        widget=django_filters.widgets.RangeWidget(
            attrs={'type':'date', 'class': 'col-md-2 form-item-half'}
        )
    )
    @property
    def qs(self):
        queryset = super(LedgerDataFilter, self).qs
        users = getUsersFromGroup(self.request.user)
        return queryset.filter(user__in=users).values(*self.values)