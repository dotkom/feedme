from django.forms import ModelForm
from models import Pizza, Order, AdminOrderLimit, AdminOrders, AdminUsers

class PizzaForm(ModelForm):

    class Meta:
        model = Pizza
        exclude = ('order', 'user')
       
    def __init__(self, *args, **kwargs):
        super(PizzaForm, self).__init__(*args, **kwargs)
        self.fields['buddy'].empty_label = None 

class AdminOrdersForm(ModelForm):
    name=u'orders'

    class Meta:
        model = AdminOrders

class AdminUsersForm(ModelForm):
    name=u'users'

    class Meta:
        model = AdminUsers

class AdminOrderLimitForm(ModelForm):
    name=u'order limit'

    class Meta:
        model = AdminOrderLimit

class NewOrderForm(ModelForm):
    name=u'new order'

    class Meta:
        model = Order
        fields = ('date',)


