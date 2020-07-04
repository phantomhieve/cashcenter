from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django_filters.views import FilterView
from django.views import View
from django.contrib.auth.decorators import user_passes_test

from .models import RatelistData, RatelistDataHelper
from .forms import RatelistDataFormset, RatelistForm
from .filters import RatelistDataFilter

class RatelistListView(FilterView):
    model = RatelistData
    template_name = 'ratelist/list_ratelist.html'
    filterset_class  = RatelistDataFilter
    paginate_by=5

    def get(self, *args, **kwargs):
        if not self.request.user.is_staff:
            return redirect('/')
        return super(RatelistListView, self).get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RatelistAddView(View):

    
    def get(self, *args, **kwargs):
        if not self.request.user.is_staff:
            return redirect('/')
        args = dict()
        id_ = kwargs.get('id', None)
        if id_:
            ratelist = RatelistData.objects.get(pk=id_)
            args['instance'] = id_
        else:
            ratelist = RatelistData(user=self.request.user)

        args['form'] = RatelistForm(instance=ratelist)
        args['formset'] = RatelistDataFormset(instance=ratelist)
        return render(self.request, 'ratelist/add_ratelist.html', args)
    
    
    def post(self, *args, **kwargs):
        if not self.request.user.is_staff:
            return redirect('/')
        query = self.request.GET.copy()
        query.pop('sucessful', None)
        query.pop('invalid', None)

        args = dict()
        id_ = kwargs.get('id', None)
        if id_:
            ratelist = RatelistData.objects.get(pk=id_)
            args['instance'] = id_
        else:
            ratelist = RatelistData(user=self.request.user)

        form = RatelistForm(self.request.POST, instance=ratelist)
        
        if form.is_valid():
            ratelist = form.save(commit=False)
            formset = RatelistDataFormset(self.request.POST, self.request.FILES, instance=ratelist)
            if formset.is_valid():
                ratelist.save()
                formset.save()
                args['form'] = RatelistForm(instance=ratelist)
                args['formset'] = RatelistDataFormset(instance=ratelist)
                return HttpResponseRedirect(f'/ratelist/add/{ratelist.id}/?sucessful={ratelist.hsn}&{query.urlencode()}')
        
        string = f'/ratelist/add/{id_}/' if id_ else f'/ratelist/add/'
        return HttpResponseRedirect(f"{string}?invalid=true&{query.urlencode()}")

@user_passes_test(lambda u: u.is_staff)
def ratelistDeleteView(request, id=None):
    instance = None
    if id:
        instance = get_object_or_404(RatelistData, id=id)
        instance.delete()
        return HttpResponseRedirect(f'/ratelist/?delete={instance.id}')
    return render(
        request,
        '404.html',
    )