from .models import FinancialYear
from django.utils import timezone
from django.shortcuts import redirect

class FinancialYearMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Try to get from UserFinancialYear first (Persistence)
            try:
                user_fy = request.user.financial_year_config
                request.financial_year = user_fy.financial_year
                # Sync session just in case other parts use it
                request.session['financial_year_id'] = user_fy.financial_year.id
            except Exception: # UserFinancialYear.DoesNotExist or related error
                # If not in DB, fall back to session or default, then SAVE to DB
                fy_id = request.session.get('financial_year_id')
                if fy_id:
                    try:
                        fy = FinancialYear.objects.get(id=fy_id)
                        request.financial_year = fy
                        # Create persistent entry
                        self.save_user_financial_year(request.user, fy)
                    except FinancialYear.DoesNotExist:
                        self.set_default_financial_year(request)
                else:
                    self.set_default_financial_year(request)
        else:
            request.financial_year = None
            
        response = self.get_response(request)
        return response

    def set_default_financial_year(self, request):
        today = timezone.now().date()
        fy = FinancialYear.objects.filter(start_date__lte=today, end_date__gte=today).first()
        if not fy:
            fy = FinancialYear.objects.first()
        
        request.financial_year = fy
        if fy:
            request.session['financial_year_id'] = fy.id
            if request.user.is_authenticated:
                self.save_user_financial_year(request.user, fy)
        else:
             request.session['financial_year_id'] = None

    def save_user_financial_year(self, user, fy):
        from .models import UserFinancialYear
        UserFinancialYear.objects.update_or_create(
            user=user,
            defaults={'financial_year': fy}
        )
