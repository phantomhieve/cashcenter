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
    
    # Redirect to where the user came from, or default to a safe page
    referer = request.META.get('HTTP_REFERER', '/')
    return redirect(referer)
