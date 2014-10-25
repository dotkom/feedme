from django.forms import ModelForm
from feedme.models import Order, OrderLine, ManageOrderLimit, ManageOrders, Restaurant, ManageBalance


class OrderLineForm(ModelForm):
    name = 'orderline'

    class Meta:
        model = OrderLine
        exclude = ('order', 'creator', 'paid_for')

    def __init__(self, *args, **kwargs):
        super(OrderLineForm, self).__init__(*args, **kwargs)
        self.fields['users'].empty_label = None


class OrderForm(ModelForm):
    name = u'order'

    class Meta:
        model = Order
        fields = ('date', )


class ManageOrderForm(ModelForm):
    name = u'orders'

    class Meta:
        model = ManageOrders


class ManageBalanceForm(ModelForm):
    name = u'transactions'

    class Meta:
        model = ManageBalance


class ManageOrderLimitForm(ModelForm):
    name = u'order limit'

    class Meta:
        model = ManageOrderLimit


class NewOrderForm(ModelForm):
    name = u'new order'

    class Meta:
        model = Order


class NewRestaurantForm(ModelForm):
    name = u'new restaurant'

    class Meta:
        model = Restaurant
