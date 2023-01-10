from django import forms

# Create your forms here.
class CandleForm(forms.Form):
    status = forms.BooleanField(required=False)

class NewCandleForm(forms.Form):
    candle_name = forms.CharField(max_length=50, required=True)