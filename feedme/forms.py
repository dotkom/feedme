from django.forms import ModelForm
from models import Order, OrderLine, ManageOrderLimit, ManageOrders, ManageUsers, Restaurant, Balance, ManageBalance

class OrderLineForm(ModelForm):
    name ='orderline'

    class Meta:
        model = OrderLine
        exclude = ('order', 'creator', )

    def __init__(self, *args, **kwargs):
        super(OrderLineForm, self).__init__(*args, **kwargs)
        self.fields['users'].empty_label = None

class OrderForm(ModelForm):
    name=u'order'

    class Meta:
        model = Order
        fields = ('date', )

class ManageOrderForm(ModelForm):
    name=u'orders'

    class Meta:
        model = ManageOrders

class ManageBalanceForm(ModelForm):
    name=u'users'

    class Meta:
        model = ManageBalance

class ManageOrderLimitForm(ModelForm):
    name=u'order limit'

    class Meta:
        model = ManageOrderLimit

class NewOrderForm(ModelForm):
    name=u'new order'

    class Meta:
        model = Order
        #fields = ('date',)

class NewRestaurantForm(ModelForm):
    name=u'new restaurant'

    class Meta:
        model = Restaurant
