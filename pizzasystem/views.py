from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render
from django.http import HttpResponse
from pizzasystem.models import Order, Pizza
from forms import PizzaForm

def index(request):
    order = Order.objects.all().latest()
    return render(request, 'pizzasystem/index.html', {'order' : order})

def newpizza(request):
    default_pizza = Pizza()
    form = PizzaForm(instance=default_pizza)
    return render(request, 'pizzasystem/newpizza.html', {'form' : form})

def add(request):
    form = PizzaForm(request.POST)
    if form.is_valid():
        order = Order.objects.all().latest()
        pizza = form.save(commit=False)
        pizza.user = request.user
        pizza.order = order
        ##cd = form.cleaned_data
        #soda = cd['soda']
        #dressing = cd['dressing']
        #pizza = cd['pizza']
        form.save()
        return render(request, 'pizzasystem/index.html', {'order' : order})
    return HttpResponse('Not a valid form')
    
