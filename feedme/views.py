from datetime import date, timedelta

from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum

from models import OrderLine, Order, ManageOrderLimit, Restaurant, Balance
from forms import OrderLineForm, OrderForm,  ManageOrderForm, ManageOrderLimitForm, NewOrderForm, NewRestaurantForm, ManageBalanceForm

User = get_user_model()

@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_GROUP).count() == 1)
def index(request):
    order = get_order()
    return render(request, 'index.html', {'order' : order, 'is_admin' : is_admin(request), 'can_join': not in_other_orderline(request.user)})

def orderlineview(request, orderline_id=None):
    if orderline_id == None:
        orderline = OrderLine()
    else:
        orderline = get_object_or_404(OrderLine, pk=orderline_id)

    if request.method == 'POST':
        form = OrderLineForm(request.POST, instance=orderline)
        if form.is_valid():
            new_orderline = form.save(commit=False)
            new_orderline.creator = request.user
            new_orderline.order = get_order()
            if check_orderline(request, new_orderline, orderline_id):
                new_orderline.save()
                form.save_m2m() # Manually save the m2m relations when using commit=False
                return redirect(index)
            else:
                new_orderline = OrderLineForm(request.POST, auto_id=True)
        else:
            new_orderline = OrderLineForm(request.POST, auto_id=True)
    else:
        if orderline_id:
            form = OrderLineForm(instance=orderline)
            form.fields["users"].queryset = get_order().available_users()
        else:
            form = OrderLineForm(instance=orderline)
            form.fields["users"].queryset = get_order().available_users()
    return render(request, 'orderview.html', {'form' : form, 'is_admin' : is_admin(request)})

def edit_orderline(request, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    if not is_in_current_order('orderline', orderline_id):
        messages.error(request, 'you can not edit orderlines from old orders')
    elif orderline.creator != request.user: # and orderline.buddy != request.user:
        messages.error(request, 'You need to be the creator')
        return redirect(index)
    return orderlineview(request, orderline_id)

def delete_orderline(request, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    if not is_in_current_order('orderline', orderline_id):
        messages.error(request, 'you can not delete orderlines from old orders')
    elif orderline.creator == request.user:
        orderline.delete()
        messages.success(request,'Order line deleted')
    else:
        messages.error(request, 'You need to be the creator or the buddy')
    return redirect(index)

@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_GROUP).count() == 1)
def orderview(request, order_id=None):
    if order_id:
        order = get_object_or_404(Order, pk=order_id)
    else:
        order = Order()

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form = form.save(commit=False)
            form.creator = request.user
            form.order_line = get_order()
            form.save()
            messages.success(request, 'Order added')
            return redirect(index)

        form = OrderForm(request.POST)
    else:
        form = OrderForm(instance=order)

    return render(request, 'orderview.html', {'form' : form, 'is_admin' : is_admin(request)})

def delete_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if not is_in_current_order('order', order_id):
        messages.error(request, 'you can not delete orders from old orders')
    elif order.user == request.user:
        order.delete()
        messages.success(request,'Order deleted')
    else:
        messages.error(request, 'You need to be the creator')
    return redirect(orderview)


def edit_order(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if not is_in_current_order('order', order_id):
        messages.error(request, 'you can not edit orders from old orders')
    elif order.user != request.user:
        messages.error(request, 'You need to be the creator to edit orders')
    else:
        return orderview(request, order_id)
    return redirect(orderview)

@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_GROUP).count() == 1)
def join_orderline(request, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    #if user_is_taken(request.user):
        #messages.error(request, 'You are already part of an order line')
    #if orderline.order.buddy_system @TODO if not buddy system enabled, disable join
    if not is_in_current_order('orderline', orderline_id):
        messages.error(request, 'You can not join orderlines from old orders')
    elif in_other_orderline(request.user):
        messages.error(request, 'You cannot be in multiple orderlines')
    #elif not orderline.need_buddy:
    #    messages.error(request, 'You can\'t join that order line')
    #elif not request.user.saldo_set.all():
    #    messages.error(request, 'No saldo connected to the user')
    #elif request.user.saldo_set.get().saldo < get_order_limit().order_limit:
    #    messages.error(request, 'You have insufficent funds. Current limit : ' + str(get_order_limit().order_limit))
    else:
        orderline.users.add(request.user)
        #orderline.need_buddy = False
        orderline.save()
        messages.success(request, 'Success!')
    return redirect(index)

@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_GROUP).count() == 1)
def leave_orderline(request, orderline_id):
    orderline = get_object_or_404(OrderLine, pk=orderline_id)
    if not is_in_current_order('orderline', orderline_id):
        messages.error(request, 'You cannot leave old orders')
    elif request.user not in orderline.users.all():
        messages.error(request, 'You cannot leave since you are not in the users')
    else:
        orderline.users.remove(request.user)
        orderline.save()
        messages.success(request, 'Success - left orderline')
    return redirect(index)

# ADMIN

@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def new_order(request):
    if request.method == 'POST':
        form = NewOrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'New order line added')
            return redirect(new_order)
    else:
        form = NewOrderForm()
        form.fields["date"].initial = get_next_tuesday()

    return render(request, 'admin.html', {'form' : form, 'is_admin' : is_admin(request) })

@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def set_order_limit(request):
    limit = get_order_limit()
    if request.method == 'POST':
        form = ManageOrderLimitForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            limit.order_limit = data['order_limit']
            limit.save()
            messages.success(request,'Order limit changed')
            return redirect(set_order_limit)
    else:
        form = ManageOrderLimitForm(instance=limit)

    return render(request, 'admin.html', {'form' : form, 'is_admin' : is_admin(request) })

@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def manage_users(request, balance=None):
    if request.method == 'POST':
        if balance == None:
            balance = get_or_create_balance(request.user)
        else:
            balance = get_object_or_404(Balance, balance)
        form = ManageBalanceForm(request.POST)
        form.user_funds = balance
        if form.is_valid():
            data = form.cleaned_data
            handle_deposit(data)
            messages.success(request, 'Deposit successful')
            return redirect(manage_users)
    else:
        form = ManageBalanceForm()
        users = []
        for user in get_orderline_users():
            users.append(get_or_create_balance(user))
        form.fields["user"].queryset = get_orderline_users()

    return render(request, 'admin.html', {'form' : form, 'is_admin' : is_admin(request) })

@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def manage_order(request):
    if request.method == 'POST':
        form = ManageOrderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            order = get_object_or_404(Order, pk=data['orders'].id)
            orderlines = order.orderline_set.all()
            total_price = 0
            for orderline in orderlines:
                total_price += orderline.price
            #handle_payment(request, data)
            #return redirect(manage_order)
            if request.POST['act'] == 'load':
                return render(request, 'manage_order.html', {'form' : form, 'is_admin' : is_admin(request), 'order': order, 'orderlines': orderlines, 'total_price': total_price})
            elif request.POST['act'] == 'pay':
                handle_payment(request, order)
                return redirect(manage_order)
        else:
            form = ManageOrderForm(request.POST)
    else:
        form = ManageOrderForm()

    orders = Order.objects.all()
    orders_price = {}
    for order in orders:
        orders_price[order] = order.get_total_sum()
    #print orders_price
    form.fields["orders"].queryset = orders
    return render(request, 'manage_order.html', {'form' : form, 'is_admin' : is_admin(request), 'orders' : orders})

@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def new_restaurant(request, restaurant_id=None):
    if restaurant_id == None:
        restaurant = Restaurant()
    else:
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)

    if request.method == 'POST':
        form = NewRestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            data = form.cleaned_data
            form.save()
            messages.success(request, "Success - restaurant added")
            return redirect(new_restaurant)
        else:
            form = NewRestaurantForm(request.POST)
    else:
        form = NewRestaurantForm(instance=restaurant)

    return render(request, 'admin.html', {'form': form, 'is_admin' : is_admin(request)})

@user_passes_test(lambda u: u.groups.filter(name=settings.FEEDME_ADMIN_GROUP).count() == 1)
def edit_restaurant(request, restaurant_id):
    order = get_object_or_404(Restaurant, pk=restaurant_id)
    return new_restaurant(request)

def get_order_limit():
    order_limit = ManageOrderLimit.objects.all()
    if order_limit:
        order_limit = ManageOrderLimit.objects.get(pk=1)
    else:
        order_limit = ManageOrderLimit()
    return order_limit

# @TODO Move logics to models

#def user_is_taken(user):
#    return user in get_order().used_users()

def check_orderline(request, form, orderline_id=None):
    orderline_exists = False
    if orderline_id == None:
        orderline = OrderLine()
        orderline.creator = User.objects.get(username=form.creator)
    else:
        orderline = get_object_or_404(OrderLine, pk=orderline_id)
        orderline_exists = True
    amount = form.price
    users = [orderline.creator]
    if orderline_exists:
        if len(orderline.users.all()) > 0:
            users.extend(orderline.users.all())
    for user in users:
        if not validate_user_funds(user, amount):
            messages.error(request, 'Unsufficient funds')
            return False

    messages.success(request, 'Order line added')
    return True
# @ToDo Refactor to a more sensible name
def validate_user_funds(user, amount):
    return get_or_create_balance(user).balance >= amount


"""
    #if not orderline_id:
        #if user_is_taken(form.user):
        #    messages.error(request, form.user.username + ' has already ordered')
        #    return False
        if user_is_taken(form.buddy):
            messages.error(request, form.buddy.username + ' has already ordered')
            return False
    if form.user == form.buddy:
        if saldo.saldo < (order_limit * 2):
           messages.error(request, u'' + form.user.username + ' has insufficient funds. Current limit: ' + str(order_limit) )
           return False
    else:
        if saldo.saldo < order_limit:
            messages.error(request,u'' + form.user.username + ' has insufficient funds. Current limit: ' + str(order_limit) )
            return False

        saldo = form.buddy.saldo_set.get()
        if saldo.saldo < order_limit:
            messages.error(request,u'' + form.buddy.username + ' has insufficient funds. Current limit: ' + str(order_limit) )
            return False"""


def handle_payment(request, order):
    orderlines = order.orderline_set.all()
    print orderlines

    paid = []
    already_paid = []
    negatives = []

    for orderline in orderlines:
        if not orderline.paid_for:
            if orderline.users.count() > 0:
                print orderline.users
                # Do some splitting
            else:
                print "balance pre %s" % orderline.creator.balance
                orderline.creator.balance.withdraw(orderline.get_total_price())
                print "balance post %s" % orderline.creator.balance
                orderline.creator.balance.save()
                orderline.paid_for = True
                orderline.save()
                paid.append(orderline.creator)
                if orderline.creator.balance < 0:
                    negatives.append(orderline.creator)
        else:
            already_paid.append(orderline.creator)
    if len(paid) > 0:
        messages.success(request, 'Paid orderlines for %s.' % ', '.join(paid))
    if len(already_paid) > 0:
        messages.error(request, 'Already paid orderlines for %s.' % ', '.join(already_paid))
    if len(negatives) > 0:
        messages.error(request, 'These users now have negative balances: %s' % ', '.join(negatives))


    """
    total_sum = data['total_sum']
    #users = order_line.used_users()
    if users:
        divided_sum = (total_sum / len(users)) * -1
        handle_saldo(users, divided_sum)
        order_line.total_sum = total_sum
        order_line.save()
        messages.success(request, 'Paid orderlines for all users')
    else:
        messages.error(request, 'Selected order contains no users')

    """

def handle_deposit(data):
    balance = data['user']
    amount = data['deposit']
    balance.deposit(amount)
    balance.save()

def get_or_create_balance(user):
    try:
        user_balance = Balance.objects.get(user=user)
        if user_balance:
            return user_balance
    except:
        balance = Balance()
        balance.user = user
        balance.save()
        return balance

def get_next_tuesday():
    today = date.today()
    day = today.weekday()
    if day < 1:
        diff = timedelta(days=(1 - day))
    elif day > 1:
        diff = timedelta(days=(7- day + 1))
    else:
        diff = timedelta(days=0)

    return today + diff

def is_admin(request):
    return request.user in User.objects.filter(groups__name=settings.FEEDME_ADMIN_GROUP)

def get_orderline_users():
    return User.objects.filter(groups__name=settings.FEEDME_GROUP).order_by('id')

def get_order():
    if Order.objects.all():
        return Order.objects.all().latest()
    else:
        return False

def is_in_current_order(order_type, order_id):
    order = get_order()
    if order_type == 'orderline':
        orderline = get_object_or_404(OrderLine, pk=order_id)
        return orderline in order.orderline_set.all()
    elif order_type == 'order':
        order = get_object_or_404(Order, pk=order_id)
        return order in order.order_set.all()
    else:
        return False

def in_other_orderline(user):
    order = get_order()
    r1 = ""
    r2 = ""
    if order:
        if order.orderline_set:
            if order.orderline_set.filter(creator=user.id):
                r1 = user == order.orderline_set.filter(creator=user.id)[0].creator
            if order.orderline_set.filter(users=user.id):
                r2 = user in order.orderline_set.filter(users=user.id)[0].users.all()
    return r1 or r2
