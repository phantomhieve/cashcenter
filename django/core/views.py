import json
import logging
from urllib.parse import urlparse, urlunparse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods
from .forms import FinancialPasswordChangeForm
from .models import FinancialYear

logger = logging.getLogger(__name__)


def _verify_fy_password(user, password):
    """Check the FY password against the user's profile (hashed or plain-text fallback)."""
    if not hasattr(user, 'profile'):
        from .models import UserProfile
        UserProfile.objects.create(user=user)

    stored = user.profile.financial_year_password
    return check_password(password, stored) or password == stored


@login_required
@require_http_methods(["POST"])
def verify_financial_password(request):
    try:
        data = json.loads(request.body)
        password = data.get('password')

        if _verify_fy_password(request.user, password):
            return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'message': 'Incorrect Password'})
    except Exception as e:
        logger.warning("Error verifying financial password: %s", e)
        return JsonResponse({'success': False, 'message': 'Invalid request data'}, status=400)


@login_required
@require_http_methods(["POST"])
def switch_financial_year(request):
    """Switch the active financial year for this session (password-protected)."""
    fy_id = request.POST.get('year')
    password = request.POST.get('password')

    if not _verify_fy_password(request.user, password):
        messages.error(request, "Incorrect Financial Year Password")
    elif fy_id:
        try:
            fy = FinancialYear.objects.get(id=fy_id)
            request.session['financial_year_id'] = fy.id
            request.financial_year = fy
            messages.success(request, f"Financial Year changed to {fy}")
        except FinancialYear.DoesNotExist:
            messages.error(request, "Invalid Financial Year selected")

    referer = request.META.get('HTTP_REFERER', '/')
    parsed = urlparse(referer)
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, '', ''))
    if not url_has_allowed_host_and_scheme(clean_url, allowed_hosts={request.get_host()}):
        clean_url = '/'
    return redirect(clean_url)


@login_required
def change_financial_password(request):
    if request.method == 'POST':
        form = FinancialPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            profile = request.user.profile
            profile.financial_year_password = make_password(new_password)
            profile.save()
            messages.success(request, "Financial Year password updated successfully.")
            return redirect('ledger_base_list')
    else:
        form = FinancialPasswordChangeForm(request.user)

    return render(request, 'core/change_financial_password.html', {'form': form})
