from django.contrib.auth import get_user_model

from rest_framework import serializers

from feedme.models import Balance, Restaurant, Order, OrderLine

User = get_user_model()


class RestaurantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ('id', 'restaurant_name', 'menu_url', 'phone_number', 'email', 'buddy_system',)


class BalanceSerializer(serializers.ModelSerializer):
    balance = serializers.CharField(read_only=True)

    class Meta:
        model = Balance
        fields = ('username', 'balance')


class OrderLineSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(read_only=True)
    paid_for = serializers.BooleanField(read_only=True)
    users = BalanceSerializer(many=True, allow_null=True, read_only=True)

    class Meta:
        model = OrderLine
        fields = ('id', 'order', 'creator', 'users', 'menu_item', 'soda', 'extras', 'price', 'paid_for',)


class OrderSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer()
    total_cost = serializers.CharField(source='get_total_sum')

    class Meta:
        model = Order
        fields = ('id', 'group', 'date', 'restaurant', 'extra_costs', 'active', 'use_validation', 'total_cost')
