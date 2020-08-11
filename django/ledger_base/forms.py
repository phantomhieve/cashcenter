from django.forms import ModelForm
from .models import LedgerDataBase

class LedgerDataForm(ModelForm):
    
    class Meta:
        model   = LedgerDataBase
        exclude = ('user', )