from django.contrib.auth.models import Group

def get_feedme_groups():
    groups = Group.objects.filter(name__icontains='kom')
    return groups
