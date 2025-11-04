from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django_filters.views import FilterView
from django.views import View
from django.contrib.auth.decorators import user_passes_test
from django.urls import reverse

from .models import RatelistData, RatelistDataHelper
from .forms import RatelistDataFormset, RatelistForm
from .filters import RatelistDataFilter


class RatelistListView(FilterView):
    """View for listing and filtering rate list data."""
    
    model = RatelistData
    template_name = 'ratelist/list_ratelist.html'
    filterset_class = RatelistDataFilter
    paginate_by = 5

    def get(self, *args, **kwargs):
        """Check if user is staff before allowing access."""
        if not self.request.user.is_staff:
            return redirect('/')
        return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add context data."""
        context = super().get_context_data(**kwargs)
        return context


class RatelistAddView(View):
    """View for adding or updating rate list data."""
    
    def get(self, *args, **kwargs):
        """Handle GET requests."""
        if not self.request.user.is_staff:
            return redirect('/')
        
        context = {}
        id_ = kwargs.get('id', None)
        
        if id_:
            ratelist = get_object_or_404(RatelistData, pk=id_)
            context['instance'] = id_
        else:
            ratelist = RatelistData(user=self.request.user)

        context['form'] = RatelistForm(instance=ratelist)
        context['formset'] = RatelistDataFormset(instance=ratelist)
        return render(self.request, 'ratelist/add_ratelist.html', context)
    
    def post(self, *args, **kwargs):
        """Handle POST requests."""
        if not self.request.user.is_staff:
            return redirect('/')
        
        query = self.request.GET.copy()
        query.pop('sucessful', None)
        query.pop('invalid', None)

        context = {}
        id_ = kwargs.get('id', None)
        
        if id_:
            ratelist = get_object_or_404(RatelistData, pk=id_)
            context['instance'] = id_
        else:
            ratelist = RatelistData(user=self.request.user)

        form = RatelistForm(self.request.POST, instance=ratelist)
        
        if form.is_valid():
            ratelist = form.save(commit=False)
            formset = RatelistDataFormset(
                self.request.POST,
                self.request.FILES,
                instance=ratelist
            )
            if formset.is_valid():
                ratelist.save()
                formset.save()
                context['form'] = RatelistForm(instance=ratelist)
                context['formset'] = RatelistDataFormset(instance=ratelist)
                redirect_url = reverse('ratelist_update', args=[ratelist.id]) if id_ else reverse('ratelist_add')
                return HttpResponseRedirect(
                    f'{redirect_url}?sucessful={ratelist.hsn}&{query.urlencode()}'
                )
        
        redirect_url = reverse('ratelist_update', args=[id_]) if id_ else reverse('ratelist_add')
        return HttpResponseRedirect(f"{redirect_url}?invalid=true&{query.urlencode()}")

@user_passes_test(lambda u: u.is_staff)
def ratelistDeleteView(request, id=None):
    """View for deleting rate list data."""
    if id:
        instance = get_object_or_404(RatelistData, id=id)
        instance_id = instance.id
        instance.delete()
        return HttpResponseRedirect(reverse('ratelist_list') + f'?delete={instance_id}')
    return render(request, '404.html')