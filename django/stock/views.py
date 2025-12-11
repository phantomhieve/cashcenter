from django.shortcuts import render, redirect, get_object_or_404
from django_filters.views import FilterView
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse
from django.db.models import Sum, F

from .models import StockData
from .filters import StockDataFilter
from .forms import StockDataForm


class StockListView(FilterView):
    """View for listing and filtering stock data."""
    
    model = StockData
    template_name = 'stock/list_stock.html'
    filterset_class = StockDataFilter
    paginate_by = 10

    def get(self, *args, **kwargs):
        """Check if user is staff before allowing access."""
        if not self.request.user.is_staff:
            return redirect('/')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add total stock value to context using database aggregation."""
        context = super().get_context_data(**kwargs)
        # Use database aggregation instead of Python sum for better performance
        queryset = self.filterset_class(self.request.GET, queryset=self.model.objects.filter(user=self.request.user)).qs
        total = queryset.aggregate(
            total=Sum(F('pcs_mtr') * F('rate'))
        )['total'] or 0
        context["total"] = total
        return context

@user_passes_test(lambda u: u.is_staff)
def stockAddView(request, id=None):
    """View for adding or updating stock data."""
    instance = None
    if id:
        instance = get_object_or_404(StockData, id=id)
    
    if request.method == 'POST':
        form = StockDataForm(request.POST, instance=instance)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.user = request.user
            stock.financial_year = getattr(request, 'financial_year', None)
            stock.save()
            return HttpResponseRedirect(reverse('stock_list'))
        return render(request, '404.html')
    
    context = {
        'form': StockDataForm(instance=instance),
        'instance': instance.id if instance else None
    }
    return render(request, 'stock/add_stock.html', context)


@user_passes_test(lambda u: u.is_staff)
def stockDeleteView(request, id=None):
    """View for deleting stock data."""
    if id:
        instance = get_object_or_404(StockData, id=id)
        hsn = instance.hsn
        instance.delete()
        return HttpResponseRedirect(reverse('stock_list') + f'?lr-no={hsn}')
    return render(request, '404.html')


@user_passes_test(lambda u: u.is_staff)
def autoComplete(request):
    """Provide autocomplete suggestions for stock fields."""
    q = request.GET.get('q')
    field = request.GET.get('field')
    
    if q and field:
        lookup = {f'{field}__icontains': q}
        # Use distinct() at database level instead of set() in Python
        data = StockData.objects.filter(
            **lookup,
            user=request.user,
            financial_year=getattr(request, 'financial_year', None)
        ).values_list(field, flat=True).distinct()[:10]
        
        return JsonResponse(list(data), safe=False)
    
    return JsonResponse([], safe=False)