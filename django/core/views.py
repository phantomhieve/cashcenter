from urllib.parse import urlparse, urlunparse
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from .models import FinancialYear, SystemConfig, UserFinancialYear
from django.contrib import messages
from django.http import JsonResponse
import json

from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render
from .forms import FinancialPasswordChangeForm

@login_required
@require_http_methods(["POST"])
def verify_financial_password(request):
    try:
        data = json.loads(request.body)
        password = data.get('password')
        
        if not hasattr(request.user, 'profile'):
             return JsonResponse({'success': False, 'message': 'User profile not found'})

        real_stored_pwd = request.user.profile.financial_year_password
        if check_password(password, real_stored_pwd) or password == real_stored_pwd:
             return JsonResponse({'success': True})
        else:
             return JsonResponse({'success': False, 'message': 'Incorrect Password'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@require_http_methods(["POST"])
def switch_financial_year(request):
    """View to switch the active financial year with password protection."""
    fy_id = request.POST.get('year')
    password = request.POST.get('password')
    
    # 1. Verify Password against UserProfile
    # Note: request.user.profile should exist due to signal, but we can be safe:
    if not hasattr(request.user, 'profile'):
        # Just in case signals didn't catch an old user until now
        from .models import UserProfile
        UserProfile.objects.create(user=request.user)
    
    user_password_config = request.user.profile.financial_year_password
    
    if not check_password(password, user_password_config):
        # Fallback check: if the user hasn't set a hashed password yet (e.g. default 'admin' is plain text in db?)
        # Standard django check_password handles plain text if not hashed? No, it expects encoded. 
        # But our default was 'admin', which is plain text.
        # Wait, check_password compares (plain_text, encoded_hash). 
        # If 'admin' is stored as plain text in the DB CharField, check_password will fail if it expects a hash structure.
        # However, for simplicity and backward compat with the previous SystemConfig which likely stored plain text or hash
        # The previous code used: check_password(password, config.financial_year_password)
        # If config.financial_year_password was 'admin' plain text, check_password might fail or return False depending on how it treats non-hash strings.
        # Actually Django's check_password return False if the hash format is invalid (like plain text).
        # Let's assume for now we WANT hashed passwords, but the default 'admin' might need to be handled.
        # If the stored password == the input password (plain text match), we accept it (migration phase)
        # OR we just use the same logic as before.
        
        # If the stored value matches input exactly (plain text fallback)
        if password == user_password_config:
             pass # valid
        else:
             messages.error(request, "Incorrect Financial Year Password")
             # Return early? logic below was "if not ... error else ..."
             # Let's restructure to match original flow
             
    # Reworking the flow to match original indentation structure but with new logic
    # We need to determine Validity first
    is_valid = False
    
    if hasattr(request.user, 'profile'):
         real_stored_pwd = request.user.profile.financial_year_password
         if check_password(password, real_stored_pwd) or password == real_stored_pwd:
             is_valid = True
    else:
         # Should not happen with our lazy create above, but safety
         # Fallback to system default if profile completely missing? No, create above handles it.
         pass

    if not is_valid:
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

@login_required
def change_financial_password(request):
    if request.method == 'POST':
        form = FinancialPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            # Update password
            profile = request.user.profile
            profile.financial_year_password = make_password(new_password)
            profile.save()
            messages.success(request, "Financial Year password updated successfully.")
            return redirect('ledger_base_list') # Redirect to home/dashboard
    else:
        form = FinancialPasswordChangeForm(request.user)
    
    return render(request, 'core/change_financial_password.html', {'form': form})

