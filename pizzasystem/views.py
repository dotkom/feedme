from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render
from django.http import HttpResponse
from pizzasystem.models import PizzaSystem

def index(request):
    orders = PizzaSystem.objects.all()
    return render('pizzasystem/index.html', {'orders' : orders})

def newpizza(request):
    user = request.user
    pizza = PizzaSystem()
    return render('pizzasystem/newpizza.html', {'pizza' : pizza, 'user' : user})
    
