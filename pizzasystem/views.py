from django.contrib import messages
from django.contrib.auth.models import Group
        
from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from pizzasystem.models import Order, Pizza, Saldo, AdminOrderLimit, AdminUsers, AdminOrders
from forms import PizzaForm, AdminOrdersForm, AdminOrderLimitForm, NewOrderForm, AdminUsersForm
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
            if check_saldo(request, form):
                form.save()
                return redirect(index)
            else:
                form = PizzaForm(request.POST, auto_id=True)
        else:
            form = PizzaForm(request.POST, auto_id=True)
    else:
#TODO fix
        if pizza_id:
            form = PizzaForm(instance=pizza)
            form.fields["buddy"].queryset = Order.objects.all().latest().free_users(pizza.buddy, pizza.user)
        else: 
            form = PizzaForm(instance=pizza, initial={'buddy' : request.user})
            form.fields["buddy"].queryset = Order.objects.all().latest().free_users()
    
    return render(request, 'pizzaview.html', {'form' : form, 'is_admin' : is_admin(request)})

@user_passes_test(lambda u: u.groups.filter(name='pizzaadmin').count() == 1)
def admin(request):
    order_limit = get_order_limit()

    if request.method == 'POST':
        action = request.GET.get('f', None)
        if action == 'orders':
            form = AdminOrdersForm(request.POST)
        elif action == 'users':
            form = AdminUsersForm(request.POST)
        elif action == 'order limit':
            form = AdminOrderLimit(request.POST, instance=order_limit)
        elif action == 'new order':
            form = NewOrderForm(request.POST) 
        
        if form.is_valid():
            data = form.cleaned_data
            if action == 'orders':
                handle_payment(data)
                messages.success(request, 'Payment successful')
            elif action == 'users':
                handle_deposit(data)
                messages.success(request, 'Deposit successful')
            else:
                form.save()
                messages.success(request, 'success')
            return redirect(admin)
        else:
            forms = []
            forms.append(form)
            return render(request, 'admin.html', {'forms' : forms })
    else:
        validate_or_create_saldo()
        forms = []

        new_order_form = NewOrderForm()
        new_order_form.fields["date"].initial = get_next_wednesday()
        forms.append(new_order_form)

        order_form = AdminOrdersForm(instance=AdminOrders()) 
        order_form.fields["orders"].queryset = Order.objects.filter(total_sum=0)
        forms.append(order_form)

        users_form = AdminUsersForm(instance=AdminUsers())
        users_form.fields["users"].queryset = get_pizza_users()
        forms.append(users_form)
        
        forms.append( AdminOrderLimitForm(instance=order_limit))
        return render(request, 'admin.html', {'forms' : forms})

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
    if request.method == 'POST':
        form = AdminOrderLimitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Order limit changed')
            return redirect(order_limit)
    else:
        form = AdminOrderLimitForm(instance=get_order_limit())

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
        form = AdminUsersForm()
        form.fields["users"].queryset = get_pizza_users()
    
    return render(request, 'admin/admin.html', {'form' : form })

@user_passes_test(lambda u: u.groups.filter(name='pizzaadmin').count() == 1)
def orders(request):
    if request.method == 'POST':
        form = AdminOrdersForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            handle_payment(data)
            messages.success(request, 'Payment handeled')
            return redirect(orders)
    else:
        form = AdminOrdersForm()
        form.fields["orders"].queryset = Order.objects.filter(total_sum=0)
    
    return render(request, 'admin/admin.html', {'form' : form })

@login_required
@user_passes_test(lambda u: u.groups.filter(name='pizza').count() == 1)
def edit(request, pizza_id):
    pizza = get_object_or_404(Pizza, pk=pizza_id)
    if pizza.user != request.user and pizza.buddy != request.user:
        return HttpResponse("Permission denied")
    return pizzaview(request, pizza_id)

@login_required
@user_passes_test(lambda u: u.groups.filter(name='pizza').count() == 1)
def delete(request, pizza_id):
    pizza = get_object_or_404(Pizza, pk=pizza_id)
    if pizza.user != request.user and pizza.buddy != request.user:
        return HttpResponse("Permission denied")
    pizza.delete()
    return redirect('/pizza') 

@login_required
@user_passes_test(lambda u: u.groups.filter(name='pizza').count() == 1)
def join(request, pizza_id):
    pizza = get_object_or_404(Pizza, pk=pizza_id)
    if pizza.user != pizza.buddy:
        return HttpResponse("Permission denied")
    if request.user.saldo_set.get().saldo < get_order_limit().order_limit:
        return HttpResponse(request.user.username + ' Insufficient funds')
    pizza.buddy = request.user
    pizza.need_buddy = False
    pizza.save()
    return redirect('/pizza') 

def get_order_limit():
    order_limit = AdminOrderLimit.objects.all()
    if order_limit:
        order_limit = OrderLimit.objects.get(pk=1)
    else:
        order_limit = AdminOrderLimit()
    return order_limit

def check_saldo(request, form):
    validate_or_create_saldo()
    order_limit = get_order_limit().order_limit
    saldo = form.user.saldo_set.get()

    if form.user == form.buddy:
        if saldo.saldo < (order_limit * 2):
           messages.error(request, u'' + form.user.username + ' has insufficient funds. Current limmit: ' + str(order_limit) )
           return False
    else:
        if saldo.saldo < order_limit:
            messages.error(request,u'' + form.user.username + ' has insufficient funds. Current limmit: ' + str(order_limit) )
            return False

        saldo = form.buddy.saldo_set.get()
        if saldo.saldo < order_limit:
            messages.error(request,u'' + form.buddy.username + ' has insufficient funds. Current limmit: ' + str(order_limit) )
            return False
    messages.success(request, 'Pizza added')
    return True

#Depricated
def is_allowed(request):
    allowed = Order.objects.all().latest().pizza_users()
    for user in allowed:
        if user == request.user:
            return True
    return False

#depricated
def denied():
    return HttpResponse('Permission denied')

def handle_payment(data):
    order = data['orders']
    if(order):
        total_sum = data['total_sum']
        users = order.used_users()
        divided_sum = (total_sum / len(users)) * -1
        handle_saldo(users, divided_sum)
        order.total_sum = total_sum
        order.save()
    else:
        print "Ikke noe order valgt"

def handle_deposit(data):
    users = data['users']
    deposit = data['add_value']

    handle_saldo(users, deposit) 
    
def handle_saldo(users, value):
    for user in users:
        saldo = user.saldo_set.get()
        saldo.saldo += value
        saldo.save()

def validate_or_create_saldo():
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
 
