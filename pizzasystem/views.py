from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render
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

def add(request):
    if is_allowed(request):
        form = PizzaForm(request.POST)
        if form.is_valid():
            order = Order.objects.all().latest()
            pizza = form.save(commit=False)
            pizza.user = request.user
            pizza.order = order
            form.save()
            return render(request, 'pizzasystem/index.html', {'order' : order})
        return HttpResponse('Not a valid form')
    return HttpResponse('Nope')
    

def is_allowed(request):
    allowed = Order.objects.all().latest().pizza_users()
    for user in allowed:
        if user == request.user:
            return True
    return False
