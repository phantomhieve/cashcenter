from .models import FinancialYear
from django.utils import timezone


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
                    self._set_default(request)
            else:
                self._set_default(request)
        else:
            request.financial_year = None

        return self.get_response(request)

    def _set_default(self, request):
        today = timezone.now().date()
        fy = FinancialYear.objects.filter(
            start_date__lte=today, end_date__gte=today
        ).first()
        if not fy:
            fy = FinancialYear.objects.first()

        request.financial_year = fy
        request.session['financial_year_id'] = fy.id if fy else None
