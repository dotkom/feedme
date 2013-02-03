from django import forms
from models import Pizza

class PizzaForm(forms.Form):
    #buddy = forms.ForeignField()
    soda = forms.CharField()
    dressing = forms.BooleanField()
    pizza = forms.IntegerField()
