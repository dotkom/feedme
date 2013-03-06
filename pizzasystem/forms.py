from django.forms import ModelForm
from models import Pizza, Admin, Order, OrderLimit

class PizzaForm(ModelForm):

    class Meta:
        model = Pizza
        exclude = ('order', 'user')

class AdminForm(ModelForm):
    
    class Meta:
        model = Admin

class OrderLimitForm(ModelForm):

    class Meta:
        model = OrderLimit

