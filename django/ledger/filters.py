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
        ('bill_ammount', 'Bill Amount'),
    )

    class Meta:
        model = LedgerData
        fields = {
            'l_r_no':['icontains'],
            'status':['exact'],
            'delivery':['exact'],
            'reciept':['icontains'],
            'bale_no':['icontains'],
            'item':['icontains']
        }

    # Status 
    STATUS_CHOICES = (
        ('', 'All'),
        ('True', 'Done'),
        ('False', 'Pending')
    )
    status = django_filters.ChoiceFilter(
        field_name='status',  
        choices=STATUS_CHOICES, 
        empty_label=None
    )

    # Extra field
    DELIVERY_CHOICES = (
        ('True', 'Delivered'),
        ('False', 'Not-Delivered')
    )
    d_status = django_filters.ChoiceFilter(
        label='d_status',
        choices=DELIVERY_CHOICES,
        method ='filter_by_delivery'
    )
    def filter_by_delivery(self, queryset, name, value):
        users = getUsersFromGroup(self.request.user)
        queryset_ = queryset.filter(user__in=users)
        if value=='True':
            queryset_ = queryset_.exclude(delivery=None)
        elif value=='False':
            queryset_ = queryset_.filter(delivery=None)
        return queryset_.values(*self.values)

    # Extra Field
    columns = django_filters.MultipleChoiceFilter(
        label  = 'Columns',
        choices = CHOICES,
        method = 'filter_by_column',
    )
    def filter_by_column(self, queryset, name, value):
        value.append('id')
        self.values = value
        users = getUsersFromGroup(self.request.user)
        return queryset.filter(user__in=users).values(*self.values)
    
    # Extra Filed
    delivery_after = django_filters.DateFilter(
        label = 'delivery_after',
        method= 'filter_delivery_after'
    )
    def filter_delivery_after(self, queryset, name, value):
        users = getUsersFromGroup(self.request.user)
        queryset_ = queryset.filter(user__in=users)
        queryset.exclude(delivery__lt=value)
        return queryset_.values(*self.values)



    # Extra Field
    l_r_date = django_filters.DateFromToRangeFilter(
        field_name='l_r_date',
        widget=django_filters.widgets.RangeWidget(
            attrs={'type':'date'}
        )
    )

    # Overriding Method
    @property
    def qs(self):
        queryset = super(LedgerDataFilter, self).qs
        users = getUsersFromGroup(self.request.user)
        return queryset.filter(user__in=users).values(*self.values)