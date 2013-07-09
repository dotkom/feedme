from django.contrib import messages
from django.contrib.auth.models import Group
        
from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from pizzasystem.models import Order, Pizza, Other, Saldo, AdminOrderLimit, AdminUsers, AdminOrders
from forms import PizzaForm, OtherForm,  AdminOrdersForm, AdminOrderLimitForm, NewOrderForm, AdminUsersForm
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date, timedelta

@user_passes_test(lambda u: u.groups.filter(name='pizza').count() == 1)
def index(request):
    order = Order.objects.all()
    if order:
        order = Order.objects.all().latest()
    return render(request, 'index.html', {'order' : order, 'is_admin' : is_admin(request)})

@user_passes_test(lambda u: u.groups.filter(name='pizza').count() == 1)
def pizzaview(request, pizza_id=None):
    if pizza_id == None:
        pizza = Pizza()
    else:
        pizza = get_object_or_404(Pizza, pk=pizza_id)

    if request.method == 'POST':
        form = PizzaForm(request.POST, instance=pizza)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            if form.need_buddy:
                form.buddy = request.user
            
            if check_request(request, form, pizza_id):
                form.save()
                return redirect(index)
            else:
                form = PizzaForm(request.POST, auto_id=True)
        else:
            form = PizzaForm(request.POST, auto_id=True)
    else:
        if pizza_id:
            form = PizzaForm(instance=pizza)
            form.fields["buddy"].queryset = Order.objects.all().latest().free_users(pizza.buddy, pizza.user)
        else: 
            form = PizzaForm(instance=pizza, initial={'buddy' : request.user})
            form.fields["buddy"].queryset = Order.objects.all().latest().free_users()
    
    return render(request, 'pizzaview.html', {'form' : form, 'is_admin' : is_admin(request)})

def edit(request, pizza_id):
    pizza = get_object_or_404(Pizza, pk=pizza_id)
    if pizza.user != request.user and pizza.buddy != request.user:
        messages.error(request, 'You need to be the creator or the buddy')
        return redirect(index)
    return pizzaview(request, pizza_id)

def delete(request, pizza_id):
    pizza = get_object_or_404(Pizza, pk=pizza_id)
    if pizza.user == request.user or pizza.buddy == request.user:
        pizza.delete()
        messages.success(request,'Pizza deleted')
    else:
        messages.error(request, 'You need to be the creator or the buddy')
    return redirect(index)

def otherview(request, other_id=None):
    if other_id:
        other = get_object_or_404(Other, pk=other_id)
    else:
        other = Other()

    if request.method == 'POST':
        form = OtherForm(request.POST)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.order = get_order()
            form.save()
            messages.success(request, 'Order added')
            return redirect(index)
        
        form = OtherForm(request.POST)
    else:
        form = OtherForm(instance=other)

    return render(request, 'otherview.html', {'form' : form, 'is_admin' : is_admin(request) })


@user_passes_test(lambda u: u.groups.filter(name='pizza').count() == 1)
def join(request, pizza_id):
    pizza = get_object_or_404(Pizza, pk=pizza_id)
    if user_is_taken(request.user):
        messages.error(request, 'You are already a part of a pizza')
    elif not pizza.need_buddy:
        messages.error(request, 'You can\'t join that pizza')
    elif not request.user.saldo_set.all():
        messages.error(request, 'No saldo connected to the user')
    elif request.user.saldo_set.get().saldo < get_order_limit().order_limit:
        messages.error(request, 'You have insufficent funds. Current limit : ' + str(get_order_limit().order_limit))
    else:
        pizza.buddy = request.user
        pizza.need_buddy = False
        pizza.save()
        messages.success(request, 'Success!')
    return redirect(index) 

# ADMIN

@user_passes_test(lambda u: u.groups.filter(name='pizzaadmin').count() == 1)
def new_order(request):
    if request.method == 'POST':
        form = NewOrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'New order added')
            return redirect(new_order)
    else:
        form = NewOrderForm()
        form.fields["date"].initial = get_next_wednesday()

    return render(request, 'admin/admin.html', {'form' : form })

@user_passes_test(lambda u: u.groups.filter(name='pizzaadmin').count() == 1)
def order_limit(request):
    limit = get_order_limit()
    if request.method == 'POST':
        form = AdminOrderLimitForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            limit.order_limit = data['order_limit']
            limit.save()
            messages.success(request,'Order limit changed')
            return redirect(order_limit)
    else:
        form = AdminOrderLimitForm(instance=limit)

    return render(request, 'admin/admin.html', {'form' : form })

@user_passes_test(lambda u: u.groups.filter(name='pizzaadmin').count() == 1)
def users(request):
    if request.method == 'POST':
        form = AdminUsersForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            handle_deposit(data)
            messages.success(request, 'Deposit successful')
            return redirect(users)
    else:
        validate_saldo()
        form = AdminUsersForm()
        form.fields["users"].queryset = get_pizza_users()
    
    return render(request, 'admin/admin.html', {'form' : form })

@user_passes_test(lambda u: u.groups.filter(name='pizzaadmin').count() == 1)
def orders(request):
    if request.method == 'POST':
        form = AdminOrdersForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            handle_payment(request, data)
            return redirect(orders)
        else:
            form = AdminOrdersForm(request.POST)
    else:
        form = AdminOrdersForm()
    
    unhandeled_orders = Order.objects.filter(total_sum=0)
    form.fields["orders"].queryset = unhandeled_orders
    return render(request, 'admin/admin.html', {'form' : form, 'orders' : unhandeled_orders})

def get_order_limit():
    order_limit = AdminOrderLimit.objects.all()
    if order_limit:
        order_limit = AdminOrderLimit.objects.get(pk=1)
    else:
        order_limit = AdminOrderLimit()
    return order_limit

#methods

def user_is_taken(user):
    return user in Order.objects.all().latest().used_users()

def check_request(request, form, pizza_id=None):
    validate_saldo()
    order_limit = get_order_limit().order_limit
    saldo = form.user.saldo_set.get()

    if not pizza_id:
        if user_is_taken(form.user):
            messages.error(request, form.user.username + ' has already ordered a pizza')
            return False
        if user_is_taken(form.buddy):
            messages.error(request, form.buddy.username + ' has already ordered a pizza')
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
            return False
    messages.success(request, 'Pizza added')
    return True

def handle_payment(request, data):
    order = data['orders']
    total_sum = data['total_sum']
    users = order.used_users()
    if users:
        divided_sum = (total_sum / len(users)) * -1
        handle_saldo(users, divided_sum)
        order.total_sum = total_sum
        order.save()
        messages.success(request, 'Payment handeled')
    else:
        messages.error(request, 'Selected order contains no users')

def handle_deposit(data):
    users = data['users']
    deposit = data['add_value']

    handle_saldo(users, deposit) 
    
def handle_saldo(users, value):
    for user in users:
        saldo = user.saldo_set.get()
        saldo.saldo += value
        saldo.save()

def validate_saldo():
    users = get_pizza_users()
    for user in users:
        saldo = user.saldo_set.all()
        if not saldo:
            saldo = Saldo()
            saldo.user = user
            saldo.save()
        
def get_next_wednesday():
    today = date.today()
    day = today.weekday()
    if day < 2:
        diff = timedelta(days=(2 - day))
    elif day > 2:
        diff = timedelta(days=(7- day + 2))
    else:
        diff = timedelta(days=7)
    
    return today + diff

def is_admin(request):
    return request.user in Group.objects.get(name="pizzaadmin").user_set.all()

def get_pizza_users():
   return Group.objects.get(name='pizza').user_set.all()

def get_order():
    return Order.objects.all().latest()
