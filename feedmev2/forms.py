from django.forms import ModelForm
from models import Order, OrderLine, ManageOrderLimit, ManageOrders, ManageUsers

class OrderLineForm(ModelForm):
    name ='orderline'

    class Meta:
        model = OrderLine
        exclude = ('order', 'creator', 'buddy_system')

    def __init__(self, *args, **kwargs):
        super(OrderLineForm, self).__init__(*args, **kwargs)
        #self.fields['users'].empty_label = None

class OrderForm(ModelForm):
    name=u'order'

    class Meta:
        model = Order
        fields = ('date', )



class ManageOrderForm(ModelForm):
    name=u'orders'

    class Meta:
        model = ManageOrders

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
