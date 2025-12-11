from urllib.parse import urlparse, urlunparse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import FinancialYear, SystemConfig, UserFinancialYear
from django.contrib import messages

from django.contrib.auth.hashers import check_password

@login_required
@require_http_methods(["POST"])
def switch_financial_year(request):
    """View to switch the active financial year with password protection."""
    fy_id = request.POST.get('year')
    password = request.POST.get('password')
    
    # 1. Verify Password
    config = SystemConfig.objects.first()
    if not config or not check_password(password, config.financial_year_password):
        messages.error(request, "Incorrect Financial Year Password")
    else:
        # 2. Update Persisted Year
        if fy_id:
            try:
                fy = FinancialYear.objects.get(id=fy_id)
                UserFinancialYear.objects.update_or_create(
                    user=request.user,
                    defaults={'financial_year': fy}
                )
                request.financial_year = fy # Update current request
                request.session['financial_year_id'] = fy.id
                messages.success(request, f"Financial Year changed to {fy}")
            except FinancialYear.DoesNotExist:
                messages.error(request, "Invalid Financial Year selected")

    # Redirect to where the user came from, but clear query params (filters)
    referer = request.META.get('HTTP_REFERER', '/')
    parsed = urlparse(referer)
    # Reconstruct URL without query and fragment
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, '', ''))
    
    return redirect(clean_url)
