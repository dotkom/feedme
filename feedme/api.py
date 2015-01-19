from tastypie.resources import ModelResource
from feedme.models import OrderLine

class OrderLineResource(ModelResource):
    class Meta:
        queryset = OrderLine.objects.all()
        resource_name = 'orderline'
