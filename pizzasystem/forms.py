from django.forms import ModelForm
from models import Pizza

class PizzaForm(ModelForm):
    #buddy = forms.ForeignField()
    #soda = forms.CharField()
    #dressing = forms.BooleanField()
    #pizza = forms.IntegerField()
    
    class Meta:
        model = Pizza
        exclude = ('order', 'user')
