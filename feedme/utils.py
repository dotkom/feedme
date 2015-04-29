from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from feedme.models import Order

def get_feedme_groups():
    order_ctype = ContentType.objects.get_for_model(Order)
    permission = Permission.objects.get(codename='view_order', content_type=order_ctype)
    return [g for g in Group.objects.all() if permission in g.permissions.all()]