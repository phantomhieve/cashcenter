from django.forms import ModelForm
from django.forms.models import inlineformset_factory
from .models import RatelistData, RatelistDataHelper


class RatelistDataHelperForm(ModelForm):
    """Form for RatelistDataHelper instances."""
    
    class Meta:
        model = RatelistDataHelper
        exclude = ()


RatelistDataFormset = inlineformset_factory(
    RatelistData,
    RatelistDataHelper,
    form=RatelistDataHelperForm,
    extra=1,
    fields=('p_price', 'p_date', 's_price', 's_date',),
    can_delete=True
)


class RatelistForm(ModelForm):
    """Form for creating and updating RatelistData instances."""
    
    class Meta:
        model = RatelistData
        exclude = ['user', ]