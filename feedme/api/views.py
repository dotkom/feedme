from rest_framework import viewsets, mixins, status
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from feedme.models import Balance, Order, OrderLine
from feedme.api.serializers import OrderSerializer, OrderLineSerializer, BalanceSerializer
from feedme.api.validators import validate_funds


class OrderViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (AllowAny,)


class OrderLineViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                       mixins.CreateModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = OrderLine.objects.all()
    serializer_class = OrderLineSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    filter_fields = ('id', 'order',)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        validate_funds(request.user, float(request.data['price']))
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @detail_route(methods=['put'], permission_classes=[IsAuthenticatedOrReadOnly])
    def join(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        validate_funds(request.user, instance.price)
        instance.users.add(request.user)
        instance.save()

        serializer = self.serializer_class(initial=instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @detail_route(methods=['put'], permission_classes=[IsAuthenticatedOrReadOnly])
    def leave(self, request, pk=None):
        instance = self.queryset.get(pk=pk)
        instance.users.remove(request.user)
        instance.save()

        serializer = self.serializer_class(initial=instance)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BalanceViewSet(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
