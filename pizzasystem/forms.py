from django.forms import ModelForm
from models import Pizza, Admin, Order

class PizzaForm(ModelForm):
    
    class Meta:
        model = Pizza
        exclude = ('order', 'user')

class AdminForm(ModelForm):
    
    class Meta:
        model = Admin

