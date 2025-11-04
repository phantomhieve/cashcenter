from django.forms import ModelForm
from .models import LedgerData


class LedgerDataForm(ModelForm):
    """Form for creating and updating LedgerData instances."""
    
    class Meta:
        model = LedgerData
        exclude = ('user',)

