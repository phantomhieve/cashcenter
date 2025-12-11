from .models import FinancialYear
from django.utils import timezone
from django.shortcuts import redirect

class FinancialYearMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            fy_id = request.session.get('financial_year_id')
            if fy_id:
                try:
                    request.financial_year = FinancialYear.objects.get(id=fy_id)
                except FinancialYear.DoesNotExist:
                    # Session has stale ID, fall back to default
                    self.set_default_financial_year(request)
            else:
                self.set_default_financial_year(request)
        else:
            request.financial_year = None
            
        response = self.get_response(request)
        return response

    def set_default_financial_year(self, request):
        today = timezone.now().date()
        # Find the FY that covers today. If multiple, pick the first (shouldn't happen with proper data)
        # If none covers today, pick the most recent one.
        fy = FinancialYear.objects.filter(start_date__lte=today, end_date__gte=today).first()
        if not fy:
            fy = FinancialYear.objects.first() # Just pick the latest one available if no match
        
        request.financial_year = fy
        if fy:
            request.session['financial_year_id'] = fy.id
        else:
             request.session['financial_year_id'] = None
