import django_filters
from .models import LedgerData
from user.models import UserGroup

DEFAULT = (
    'l_r_no',
    'no_of_bale',
    'bale_no',
    'item',
    'transport',
    'status',
    'id'
)


def filterData(values, user, queryset):
    user_group = UserGroup.objects.filter(primary_user=user)\
        | UserGroup.objects.filter(main_user=user)
    
    try:
        primary = user_group[0].primary_user
        main    = user_group[0].main_user
    except:
        primary = main = user

    queryset_ = queryset.filter(user=primary).values(*values)\
        | queryset.filter(user=main).values(*values)
        
    return queryset_.order_by('id')


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
        return filterData(self.values, self.request.user, queryset)

    l_r_date = django_filters.DateFromToRangeFilter(
        field_name='l_r_date',
        widget=django_filters.widgets.RangeWidget(
            attrs={'type':'date', 'class': 'col-md-2 form-item-half'}
        )
    )
    @property
    def qs(self):
        parent = super(LedgerDataFilter, self).qs
        return filterData(self.values, self.request.user, parent)