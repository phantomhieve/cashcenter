from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.views import View
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from .models import StockData
from .filters import StockDataFilter
from .forms import StockDataForm

class StockListView(ListView):
    model = StockData
    template_name = 'stock/list_stock.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter"] = StockDataFilter(
            self.request.GET, 
            queryset=self.get_queryset()
        )
        total = sum([
            stock.pcs_mtr * stock.rate
            for stock in context["filter"].qs
        ])
        context["total"] = total
        return context
    