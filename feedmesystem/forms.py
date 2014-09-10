from django.forms import ModelForm
from models import Order, OrderLine, ManageOrderLimit, ManageOrderLines, ManageUsers

class OrderLineForm(ModelForm):
    name ='orderline'

    class Meta:
        model = OrderLine
        exclude = ('order_line', 'user')

    def __init__(self, *args, **kwargs):
        super(OrderLineForm, self).__init__(*args, **kwargs)
        self.fields['buddy'].empty_label = None

class OrderForm(ModelForm):
    name=u'order'

    class Meta:
        model = Order
        fields = ('content' ,)



class ManageOrderLinesForm(ModelForm):
    name=u'orders'

    class Meta:
        model = ManageOrderLines

class ManageUsersForm(ModelForm):
    name=u'users'

    class Meta:
        model = ManageUsers

class ManageOrderLimitForm(ModelForm):
    name=u'order limit'

    class Meta:
        model = ManageOrderLimit

class NewOrderForm(ModelForm):
    name=u'new order'

    class Meta:
        model = Order
        fields = ('date',)
