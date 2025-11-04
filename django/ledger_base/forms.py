from django.forms import ModelForm
from .models import LedgerDataBase


class LedgerDataForm(ModelForm):
    """Form for creating and updating LedgerDataBase instances."""
    
    class Meta:
        model = LedgerDataBase
        exclude = ('user',)