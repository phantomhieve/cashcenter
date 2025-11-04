from django.forms import ModelForm
from .models import StockData


class StockDataForm(ModelForm):
    """Form for creating and updating StockData instances."""
    
    class Meta:
        model = StockData
        exclude = ('user',)