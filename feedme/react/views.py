from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, render

from feedme.utils import get_feedme_groups, get_or_create_balance
from feedme.views import get_order


def index(request):
    context = {}
    context['groups'] = get_feedme_groups()
    return render(request, 'feedme/react/groups.html', context)


def order(request, group=None):
    group = get_object_or_404(Group, name=group)
    active_order = get_order(group)

    context = {}
    context['api_url'] = '/feedme-api/'
    context['balance'] = get_or_create_balance(request.user)
    context['order'] = active_order
    context['user'] = request.user

    if not active_order:
        return render(request, 'feedme/404.html', context)

    return render(request, 'feedme/react/index.html', context)
