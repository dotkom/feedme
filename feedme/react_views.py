from django.shortcuts import render

from feedme.views import get_order


def react_index(request):
    context = {}
    context['order'] = get_order(request.user.groups.all()[0])
    context['username'] = request.user

    return render(request, 'feedme/react/index.html', context)
