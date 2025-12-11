from .models import FinancialYear

def financial_year_context(request):
    """Context processor to add financial year data to all templates."""
    context = {}
    if request.user.is_authenticated:
        context['financial_years'] = FinancialYear.objects.all()
        context['current_financial_year'] = getattr(request, 'financial_year', None)
    return context
