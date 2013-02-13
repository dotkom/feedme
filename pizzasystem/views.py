from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from pizzasystem.models import Order, Pizza, Admin, Saldo
from forms import PizzaForm, AdminForm

def index(request):
    if(is_allowed(request)):
        order = Order.objects.all().latest()
        return render(request, 'index.html', {'order' : order})
    return denied()

def pizzaview(request, pizza_id=None):
    if is_allowed(request):
        if pizza_id == None:
            pizza = Pizza()
        else:
            pizza = get_object_or_404(Pizza, pk=pizza_id)

        if request.method == 'POST':
            form = PizzaForm(request.POST, instance=pizza)
            if form.is_valid():
                forminstance = form.save(commit=False)
                forminstance.user = request.user
                forminstance.save()
                return index(request)
            else:
                return HttpResponse('Invalid input')
        else:
            form = PizzaForm(instance=pizza)
            form.fields["buddy"].queryset = Order.objects.all().latest().free_users()
            return render(request, 'pizzaview.html', {'form' : form})
    return denied()

def admin(request):
    if request.method == 'POST':
        form = AdminForm(request.POST, instance=Admin())
        if form.is_valid():
            data = form.cleaned_data
            if data['total_sum'] != 0:
                handle_payment(data)
            if data['add_value'] != 0:
                handle_deposit(data)
            return HttpResponseRedirect('admin.html')
        else:
            return HttpResponse('Invalid Input')
    else:
        validate_or_create_saldo()
        form = AdminForm(instance=Admin())                
        form.fields["orders"].queryset = Order.objects.filter(total_sum=0)
        form.fields["users"].queryset = Order.objects.all().latest().pizza_users()
        return render(request, 'admin.html', {'form' : form})

def edit(request, pizza_id):
    return pizzaview(request, pizza_id)

def delete(request, pizza_id):
    if is_allowed(request):
        pizza = get_object_or_404(Pizza, pk=pizza_id)
        pizza.delete()
        return index(request)
    return denied()

def is_allowed(request):
    allowed = Order.objects.all().latest().pizza_users()
    for user in allowed:
        if user == request.user:
            return True
    return False

def denied():
    return HttpResponse('Permission denied')

def handle_payment(data):
    order = data['orders']
    if(order):
        total_sum = data['total_sum']
        users = order.used_users()
        divided_sum = (total_sum / len(users)) * -1
        handle_saldo(users, divided_sum)
    else:
        print "Ikke noe order valgt"
    
def handle_deposit(data):
    users = data['users']
    deposit = data['add_value']
    
    handle_saldo(users, deposit) 
        
def handle_saldo(users, value):
    for user in users:
        if user.username == 'torhaakb' or user.username == 'kristoad':
            user.saldo_set.all().saldo = value + 1337
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
        
    
