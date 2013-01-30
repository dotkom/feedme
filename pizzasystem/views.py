from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render
from django.http import HttpResponse
from pizzasystem.models import Order, Pizza

def index(request):
    order = Order.objects.all().latest()
    return render(request, 'pizzasystem/index.html', {'order' : order})

def newpizza(request):
    default_pizza = Pizza()
    order = Order.objects.all().latest()
    default_pizza.order = order    
    return render(request, 'pizzasystem/newpizza.html', {'pizza' : default_pizza, 'order' : order})

def add(request, command):
    #p = get_object_or_404(Pizza)
    return render(request, 'Bestilt(NOT)')
    
