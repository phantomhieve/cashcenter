import django_filters
from .models import Order


class OrderFilter(django_filters.FilterSet):
    """FilterSet for filtering Order instances."""
    
    order_number__icontains = django_filters.CharFilter(
        field_name='order_number', lookup_expr='icontains'
    )
    company_name__icontains = django_filters.CharFilter(
        field_name='company_name', lookup_expr='icontains'
    )
    item__icontains = django_filters.CharFilter(
        field_name='item', lookup_expr='icontains'
    )
    status = django_filters.ChoiceFilter(
        field_name='fulfilment_status', choices=Order.FulfilmentStatus.choices
    )
    order_date = django_filters.DateFilter(field_name='order_date')
    mode = django_filters.ChoiceFilter(
        field_name='mode', choices=Order.Mode.choices
    )
    agent_name__icontains = django_filters.CharFilter(
        field_name='agent_name', lookup_expr='icontains'
    )

    class Meta:
        model = Order
        fields = []

    @property
    def qs(self):
        """Filter queryset by user and financial year."""
        queryset = super().qs
        queryset = queryset.filter(user=self.request.user)
        if getattr(self.request, 'financial_year', None):
            queryset = queryset.filter(financial_year=self.request.financial_year)
        return queryset
