from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from pizzasystem.models import Pizza

def index(request):
    orders = Pizza.objects.all()
    return render_to_response('pizzasystem/index.html', {'orders' : orders})

def newpizza(request):
    user = request.user
    pizza = Pizza()
    return render_to_response('pizzasystem/newpizza.html', {'pizza' : pizza, 'user' : user})
    
