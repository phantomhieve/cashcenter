import django_filters

from .models import LedgerData

DEFAULT = (
    'l_r_no',
    'l_r_date',
    'no_of_bale',
    'bale_no',
    'item',
    'transport',
    'status',
    'id'
)


class LedgerDataFilter(django_filters.FilterSet):
    """FilterSet for filtering LedgerData."""
    
    def __init__(self, data=None, queryset=None, request=None, prefix=None):
        self.values = DEFAULT
        super().__init__(data=data, queryset=queryset, request=request, prefix=prefix)

    CHOICES = (
        ('l_r_no', 'L R No'),
        ('no_of_bale', 'No Of Bale'),
        ('l_r_date', 'L R Date'),
        ('bale_no', 'Bale No'),
        ('hsn_code', 'HSN Code'),
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
        ('bill_ammount', 'Bill Amount'),
        ('remark', 'Remark'),
        ('status', 'Status'),
    )

    class Meta:
        model = LedgerData
        fields = {
            'l_r_no':['icontains'],
            'status':['exact'],
            'delivery':['exact'],
            'reciept':['icontains'],
            'bale_no':['icontains'],
            'item':['icontains'],
            'hsn_code':['icontains'],
            'supplier':['icontains'],
            'transport':['icontains'],
            'location':['icontains']
        }

    # Status filter
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

    # Extra field: Delivery status filter
    DELIVERY_CHOICES = (
        ('True', 'Delivered'),
        ('False', 'Not-Delivered')
    )
    d_status = django_filters.ChoiceFilter(
        label='d_status',
        choices=DELIVERY_CHOICES,
        method='filter_by_delivery'
    )
    
    def filter_by_delivery(self, queryset, name, value):
        """Filter queryset by delivery status."""
        queryset_ = queryset.filter(user=self.request.user)
        if value == 'True':
            queryset_ = queryset_.exclude(delivery=None)
        elif value == 'False':
            queryset_ = queryset_.filter(delivery=None)
        return queryset_.values(*self.values)

    # Extra Field: Column selection filter
    columns = django_filters.MultipleChoiceFilter(
        label='Columns',
        choices=CHOICES,
        method='filter_by_column',
    )
    
    def filter_by_column(self, queryset, name, value):
        """Filter queryset by selected columns."""
        value.append('id')
        self.values = value
        return queryset.filter(user=self.request.user).values(*self.values)
    
    # Extra Field: Delivery after date filter
    delivery_after = django_filters.DateFilter(
        label='delivery_after',
        method='filter_delivery_after'
    )
    
    def filter_delivery_after(self, queryset, name, value):
        """Filter queryset for deliveries after a specific date."""
        queryset_ = (
            queryset.filter(
                user=self.request.user,
                l_r_date__lt=value,
                delivery=None
            ) |
            queryset.filter(
                user=self.request.user,
                l_r_date__lt=value,
                delivery__gte=value
            )
        )
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
        """Filter queryset by user and return selected values."""
        queryset = super().qs
        return queryset.filter(user=self.request.user).values(*self.values)