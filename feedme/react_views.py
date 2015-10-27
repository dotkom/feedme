from django.shortcuts import render

from feedme.views import get_order


def react_index(request):
    return render(request, 'feedme/react/index.html', {'order': get_order(request.user.groups.all()[0])})
