from django.forms import ModelForm
from .models import LedgerData

class LedgerDataForm(ModelForm):
    
    class Meta:
        model   = LedgerData
        exclude = ('user', )

