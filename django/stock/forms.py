from django.forms import ModelForm
from .models import StockData

class StockDataForm(ModelForm):
    
    class Meta:
        model = StockData
        fields = '__all__'