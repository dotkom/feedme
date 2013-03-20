from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from pizzasystem.models import Order, Pizza, Admin, Saldo, OrderLimit
from forms import PizzaForm, AdminForm, OrderLimitForm, NewOrderForm
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import date, timedelta

@login_required
@user_passes_test(lambda u: u.groups.filter(name='pizza').count() == 1)
def index(request):
    order = Order.objects.all().latest()
    return render(request, 'index.html', {'order' : order})

@login_required
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
            return validate_request(request, form)
        else:
            return HttpResponse('Invalid input')
    else:
        form = PizzaForm(instance=pizza, initial={'buddy' : request.user})
        form.fields["buddy"].empty_label = None
        if pizza_id:
            form.fields["buddy"].queryset = Order.objects.all().latest().free_users(pizza.buddy, pizza.user)
        else: 
            form.fields["buddy"].queryset = Order.objects.all().latest().free_users()
        return render(request, 'pizzaview.html', {'form' : form})

@login_required
@user_passes_test(lambda u: u.groups.filter(name='pizzaadmin').count() == 1)
def admin(request):
    order_limit = get_order_limit()

    if request.method == 'POST':
        form = AdminForm(request.POST)
        order_limit_form = OrderLimitForm(request.POST, instance=order_limit)
        if form.is_valid() and order_limit_form.is_valid():
            data = form.cleaned_data
            if data['total_sum'] != 0:
                handle_payment(data)
            if data['add_value'] != 0:
                handle_deposit(data)
            order_limit.save()
            return HttpResponseRedirect('admin.html')
        else:
            return HttpResponse('Invalid Input')
    else:
        validate_or_create_saldo()
        form = AdminForm(instance=Admin())                
        form.fields["orders"].queryset = Order.objects.filter(total_sum=0)
        form.fields["users"].queryset = Order.objects.all().latest().pizza_users()
        order_limit_form = OrderLimitForm(instance=order_limit)
        new_order_form = NewOrderForm()
        new_order_form.fields["date"].initial = get_next_wednesday()
        return render(request, 'admin.html', {'form' : form, 'order_limit_form' : order_limit_form, 'new_order_form' : new_order_form})

@user_passes_test(lambda u: u.groups.filter(name='pizzaadmin').count() == 1)
def new_order(request):
    new_order_form = NewOrderForm(request.POST)
    if new_order_form.is_valid():
        data = new_order_form.cleaned_data
        order = Order()
        order.date = data['date']
        order.save()
        return HttpResponseRedirect('admin.html')
    return HttpResponse('Invalid input')

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
    order_limit = OrderLimit.objects.all()
    if order_limit:
        order_limit = OrderLimit.objects.get(pk=1)
    else:
        order_limit = OrderLimit()
    return order_limit

def validate_request(request, form):
    validate_or_create_saldo()
    order_limit = get_order_limit().order_limit
    saldo = form.user.saldo_set.get()

    if form.user == form.buddy:
        if saldo.saldo < (order_limit * 2):
           return HttpResponse(form.user.username + ' : insufficient funds')
    else:
        if saldo.saldo < order_limit:
            return HttpResponse(form.user.username + ' : insufficient funds')

        saldo = form.buddy.saldo_set.get()
        if saldo.saldo < order_limit:
            return HttpResponse(form.buddy.username + ' : insufficient funds')
    form.save()
    return redirect('/pizza') 

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
    users = Order.objects.all().latest().pizza_users()
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
