from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, render

from feedme.utils import get_feedme_groups

from feedme.views import get_order


def index(request):
    context = {}
    context['groups'] = get_feedme_groups()
    return render(request, 'feedme/react/groups.html', context)


def order(request, group=None):
    group = get_object_or_404(Group, name=group)

    context = {}
    context['api_url'] = '/feedme-api/'
    context['order'] = get_order(group)
    context['username'] = request.user

    return render(request, 'feedme/react/index.html', context)
