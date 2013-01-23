from django.template import Template, Context, loader, RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
#from models import PizzaSystem

def index(request):

    return render_to_response('pizzasystem/index.html')
