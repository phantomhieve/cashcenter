from urllib.parse import urlparse, urlunparse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

@login_required
@require_GET
def switch_financial_year(request):
    """View to switch the active financial year in session."""
    fy_id = request.GET.get('year')
    if fy_id:
        request.session['financial_year_id'] = fy_id
    
    # Redirect to where the user came from, but clear query params (filters)
    referer = request.META.get('HTTP_REFERER', '/')
    parsed = urlparse(referer)
    # Reconstruct URL without query and fragment
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, '', ''))
    
    return redirect(clean_url)
