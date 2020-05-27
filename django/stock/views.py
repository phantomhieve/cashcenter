from django.shortcuts import render, redirect
from django_filters.views import FilterView
from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseNotFound
from django.contrib.auth.decorators import user_passes_test

from .models import StockData
from .filters import StockDataFilter
from .forms import StockDataForm

class StockListView(FilterView):
    model            = StockData
    template_name    = 'stock/list_stock.html'
    filterset_class  = StockDataFilter
    paginate_by      = 10

    def get(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return redirect('/')
        return super(StockListView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        total = sum([
            stock.pcs_mtr * stock.rate
            for stock in context["filter"].qs
        ])
        context["total"] = total
        return context

@user_passes_test(lambda u: u.is_superuser)
def stockAddView(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(StockData, id=id)
    if request.method == 'POST':
        form = StockDataForm(request.POST, instance=instance)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.user = request.user
            stock.save()
            return HttpResponseRedirect('/stock/')
        return render(
            request,
            '404.html',
        )
    args = {
        'form': StockDataForm(instance=instance),
        'instance': instance.id if instance else None
    }
    return render(
        request,
        'stock/add_stock.html',
        args
    )

@user_passes_test(lambda u: u.is_superuser)
def stockDeleteView(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(StockData, id=id)
        instance.delete()
        return HttpResponseRedirect(f'/stock?lr-no={instance.hsn}')
    return render(
        request,
        '404.html',
    )

@user_passes_test(lambda u: u.is_superuser)
def autoComplete(request):
    if request.GET.get('q') and request.GET['field']:
        field = request.GET['field']
        q = request.GET['q']
        kwargs = {
            '{0}__{1}'.format(field, 'startswith'): q,
        }
        data = StockData.objects.filter(**kwargs, user=request.user).values_list(field, flat=True)
        json = list(set(data))
        return JsonResponse(json, safe=False)
    else:
        HttpResponse("No cookies")