from django import forms

class FilterData(forms.Form):
    template_name = 'config/filter_data.html'
    ano = forms.IntegerField(max_value=9999)
    mes = forms.IntegerField(min_value=1, max_value=12)

