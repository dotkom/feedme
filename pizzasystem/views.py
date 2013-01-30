from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404, render
from django.http import HttpResponse
from pizzasystem.models import PizzaSystem

def index(request):
    orders = PizzaSystem.objects.all()
    return render_to_response('pizzasystem/index.html', {'orders' : orders})

def newpizza(request):
    user = request.user
    pizza = PizzaSystem()
    return render_to_response('pizzasystem/newpizza.html', {'pizza' : pizza, 'user' : user})
    
