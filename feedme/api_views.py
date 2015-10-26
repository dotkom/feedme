from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly

from feedme.models import Order, OrderLine, Restaurant, Poll, Answer
from feedme.serializers import OrderSerializer, OrderLineSerializer, RestaurantSerializer


class OrderViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (AllowAny,)


class OrderLineViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer
    permission_classes = (AllowAny,)
    filter_fields = ('id', 'order',)
