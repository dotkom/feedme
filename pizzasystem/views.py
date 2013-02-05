from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from pizzasystem.models import Order, Pizza
from forms import PizzaForm

def index(request):
    if(is_allowed(request)):
        order = Order.objects.all().latest()
        return render(request, 'pizzasystem/index.html', {'order' : order})
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
            return render(request, 'pizzasystem/pizzaview.html', {'form' : form})
    return denied()
    
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
