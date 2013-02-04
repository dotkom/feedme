from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from pizzasystem.models import Order, Pizza
from forms import PizzaForm

def index(request):
    if(is_allowed(request)):
        order = Order.objects.all().latest()
        return render(request, 'pizzasystem/index.html', {'order' : order})
    return HttpResponse('Nope')

def newpizza(request):
    if is_allowed(request):
        default_pizza = Pizza()
        form = PizzaForm(instance=default_pizza)
        return render(request, 'pizzasystem/newpizza.html', {'form' : form})
    return HttpResponse('Nope')

def save(request):
    if is_allowed(request):
        form = PizzaForm(request.POST)
        if form.is_valid():
            pizza = form.save(commit=False)
            pizza.user = request.user
            pizza.order = Order.objects.all().latest()
            pizza.save()
            return index(request)
        return HttpResponse('Not a valid form')
    return HttpResponse('Nope')
    
def edit(request, pizza_id):
    if is_allowed(request):
        pizza = get_object_or_404(Pizza, pk=pizza_id)
        form = PizzaForm(instance=pizza)
        return render(request, 'pizzasystem/editpizza.html', {'form' : form})
    return HttpResponse('Nope')

def edit_function(request):
    pizza = PizzaForm(request.POST).save(commit=False)
    pizza.save()
    return index(request)
        
        


def is_allowed(request):
    allowed = Order.objects.all().latest().pizza_users()
    for user in allowed:
        if user == request.user:
            return True
    return False
