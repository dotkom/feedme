from django.conf import settings

from rest_framework import serializers

from feedme.models import Restaurant, Order, OrderLine, Poll, Answer


class FeedmeUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = settings.AUTH_USER_MODEL
        fields = ('username', 'first_name', 'last_name')


class RestaurantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Restaurant
        fields = ('id', 'restaurant_name', 'menu_url', 'phone_number', 'email', 'buddy_system',)


class OrderLineSerializer(serializers.ModelSerializer):
    creator = serializers.CharField(read_only=True)
    # creator = FeedmeUserSerializer()  # @todo fix loading actual users
    # users = serializers.CharField(many=True)

    class Meta:
        model = OrderLine
        fields = ('id', 'order', 'creator', 'users', 'menu_item', 'soda', 'extras', 'price', 'paid_for',)


class OrderSerializer(serializers.ModelSerializer):
    # orderlines = OrderLineSerializer(source="order__orderlines", many=True, read_only=True)
    restaurant = RestaurantSerializer()

    class Meta:
        model = Order
        fields = ('id', 'group', 'date', 'restaurant', 'extra_costs', 'active', 'use_validation', 'orderlines',)