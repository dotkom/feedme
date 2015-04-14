from django.contrib.auth.models import Group
from django.conf import settings

def get_feedme_groups():
    group_ids = settings.FEEDME_GROUPS
    groups = [Group.objects.get(pk=i) for i in group_ids]
    return groups
