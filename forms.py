from django import forms
from .validators import validate_ten_digits
from django.forms import formset_factory, BaseFormSet


class LoginForm(forms.Form):
    mobile_number = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Mobile Number", 
        max_length=10, 
        validators=[validate_ten_digits])


class ReturnSelectorForm(forms.Form):
    quantity = forms.ChoiceField()

    def __init__(self, *args, max_return_count, **kwargs):
        super(ReturnSelectorForm, self).__init__(*args, **kwargs)
        self.fields["quantity"].choices = ((i,i) for i in range(max_return_count))


class BaseReturnSelectorFormSet(BaseFormSet):
    max_return_counts = []

    def __init__(self, max_return_counts, *args, **kwargs):
        self.max_return_counts = max_return_counts
        super(BaseReturnSelectorFormSet, self).__init__(*args, **kwargs)

    def get_form_kwargs(self, index):
        return {'max_return_count': self.max_return_counts[index]}

ReturnSelectorFormSet = formset_factory(ReturnSelectorForm, extra=3, formset=BaseReturnSelectorFormSet)

class ExchangeSelectorForm(forms.Form):
    design = forms.ChoiceField()
    size = forms.ChoiceField()
    quantity = forms.ChoiceField()

ExchangeSelectorFormSet = formset_factory(ExchangeSelectorForm, extra=3)    
