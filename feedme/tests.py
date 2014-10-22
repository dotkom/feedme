# coding=utf-8

from datetime import date, timedelta

from django.test import TestCase

from django_dynamic_fixture import G

from django.contrib.auth.models import User, Group
from feedme.models import Order, OrderLine, Restaurant, Balance, Transaction
from feedme.views import get_or_create_balance, validate_user_funds, handle_payment
from feedme.views import in_other_orderline

# Create your tests here.

class ModelTestCase(TestCase):
    def setUp(self):
        User.objects.create(username='TestUser1')
        User.objects.create(username='FeedmeUser1')
        User.objects.create(username='AdminUser1')

        Group.objects.create(name='dotKom')
        Group.objects.create(name='feedmeadmin')

        Group.objects.get(name='dotKom').user_set.add(User.objects.get(username='FeedmeUser1'))
        Group.objects.get(name='dotKom').user_set.add(User.objects.get(username='AdminUser1'))
        Group.objects.get(name='feedmeadmin').user_set.add(User.objects.get(username='AdminUser1'))

    def test_user_in_groups(self):
        regular_user = User.objects.get(username='TestUser1')
        feedme_user = User.objects.get(username='FeedmeUser1')
        admin_user = User.objects.get(username='AdminUser1')

        self.assertEqual(regular_user.groups.filter(name='dotKom').count(), 0)
        self.assertEqual(regular_user.groups.filter(name='feedmeadmin').count(), 0)

        self.assertEqual(feedme_user.groups.filter(name='dotKom').count(), 1)
        self.assertEqual(feedme_user.groups.filter(name='feedmeadmin').count(), 0)

        self.assertEqual(admin_user.groups.filter(name='dotKom').count(), 1)
        self.assertEqual(admin_user.groups.filter(name='feedmeadmin').count(), 1)
"""
    def test_create_user_balance(self):
        feedme_user = User.objects.get(username='FeedmeUser1')
        feedme_user_balance = get_or_create_balance(feedme_user)

        self.assertEqual(feedme_user_balance.get_balance(), 0, 'Balance should be \'0\' when creating a new balance object')

    def test_deposit_and_withdraw(self):
        feedme_user = User.objects.get(username='FeedmeUser1')
        print feedme_user, get_or_create_balance(feedme_user)


        self.assertEqual(feedme_user.balance.get_balance(), 0, 'Balance should be 0 when creating a new balance object')
        self.assertEqual(feedme_user.deposit(50), True, 'Should return True for depositing with success')
        self.assertEqual(feedme_user.balance.get_balance(), 50, 'Balance should be 50 after depositing 50')
        self.assertEqual(feedme_user.deposit(-50), False, 'Should return False for depositing negative amount')
        self.assertEqual(feedme_user.balance.get_balance(), 50, 'Balance should be 50 after trying to deposit -50')
        self.assertEqual(feedme_user.withdraw(25), True, 'Should return True for withdrawing an amount you can afford')
        self.assertEqual(feedme_user.balance.get_balance(), 25, 'Balance should be 25 after withdrawing 25')
        self.assertEqual(feedme_user.withdraw(50), False, 'Should return False, but still allow dotKommers to overload their balance')
        self.assertEqual(feedme_user.balance.get_balance(), -25, 'Someone overloaded their account')
"""
class RestaurantTestCase(TestCase):
    def set_up(self):
        self.restaurant = G(Restaurant)

    def test_unicode_restaurant_name(self):
        restaurant = G(Restaurant, restaurant_name=u'ø')
        self.assertEqual(restaurant.restaurant_name, unicode(restaurant), 'The unicode name of the restaurant should be the same as the input value')

class OrderTestCase(TestCase):
    def set_up(self):
        self.restaurant = G(Restaurant)
        self.order = G(Order)
        self.orderline = G(OrderLine)

    def test_unicode_order_name(self):
        order = G(Order)
        self.assertEqual(order.__unicode__(), "%s @ %s" % (order.date.strftime("%d-%m-%Y"), order.restaurant.restaurant_name))

    def test_get_total_sum(self):
        order_1 = G(Order)
        order_2 = G(Order, extra_costs=50)
        orderline_1 = G(OrderLine, order=order_1)
        orderline_2 = G(OrderLine, order=order_1)
        orderline_3 = G(OrderLine, order=order_2)
        orderline_4 = G(OrderLine, order=order_2)

        s = orderline_1.price + orderline_2.price + order_1.extra_costs
        r = order_1.get_total_sum()
        self.assertEqual(r, s, 'Got %s, expected %s' % (r, s))
        s = orderline_3.price + orderline_4.price + order_2.extra_costs
        r = order_2.get_total_sum()
        self.assertEqual(r, s, 'Got %s, expected %s' % (r, s))

    def test_get_extra_costs(self):
        order = G(Order, extra_costs=50)
        user = G(User)
        G(OrderLine, order=order, creator=user, users=[user,])
        G(OrderLine, order=order, creator=user, users=[user,])
        self.assertEqual(order.get_extra_costs(), 25)

    def test_get_latest(self):
        order = G(Order, date=date.today() - timedelta(days=1))
        G(Order, date=date.today(), active=False)
        self.assertEqual(order.get_latest(), order)
        order.active = False
        order.save()
        self.assertFalse(order.get_latest())

class TransactionTestCase(TestCase):
    def set_up(self):
        self.user = G(User)

    def test_transactions(self):
        user = G(User)
        get_or_create_balance(user) # This creates an empty transaction!

        transaction = G(Transaction, user=user, amount=100.0)
        self.assertTrue(user.balance.get_balance(), 100.0)

        transaction = G(Transaction, user=user, amount=-100.0)
        self.assertEqual(user.balance.get_balance(), 0.0)
        self.assertEqual(user.transaction_set.count(), 3)

    def test_negative_transactions(self):
        # It is expected that people CAN go below zero!
        user = G(User)
        get_or_create_balance(user)

        transaction = G(Transaction, user=user, amount=-1)
        self.assertEqual(user.balance.get_balance(), -1.0)

    def test_balance_deposit(self):
        user = G(User)
        get_or_create_balance(user)

        self.assertTrue(user.balance.deposit(100))
        self.assertEqual(user.balance.get_balance(), 100)
        self.assertTrue(user.balance.deposit(-50))
        self.assertEqual(user.balance.get_balance(), 50)
        self.assertTrue(user.balance.withdraw(50))
        self.assertEqual(user.balance.get_balance(), 0)

class ViewPermissionsTestCase(TestCase):
    def set_up(self):
        User.objects.create(username='TestUser1')
        User.objects.create(username='FeedmeUser1')
        User.objects.create(username='AdminUser1')

        Group.objects.create(name='dotKom')
        Group.objects.create(name='feedmeadmin')

        Group.objects.get(name='dotKom').user_set.add(User.objects.get(username='FeedmeUser1'))
        Group.objects.get(name='dotKom').user_set.add(User.objects.get(username='AdminUser1'))
        Group.objects.get(name='feedmeadmin').user_set.add(User.objects.get(username='AdminUser1'))

"""
    def user_able_to_see_index(self):
        regular_user = User.objects.get(username='TestUser1')
        feedme_user = User.objects.get(username='FeedmeUser1')
        admin_user = User.objects.get(username='AdminUser1')

        self.assertEqual(1, 1)
        # @ToDo
"""

class ViewMoneyLogicTestCase(TestCase):
    def test_validate_user_funds(self):
        feedme_user = G(User)
        get_or_create_balance(feedme_user)

        feedme_user.balance.deposit(100)
        feedme_user.balance.save()

        self.assertTrue(validate_user_funds(feedme_user, 99), \
            'Should evaluate to True when user.balance >= funds.')
        self.assertTrue(validate_user_funds(feedme_user, 100), \
            'Should evaluate to True when user.balance >= funds.')
        self.assertFalse(validate_user_funds(feedme_user, 101), \
            'User does not have enough funds')


class ViewLogicTestCase(TestCase):
    def set_up(self):
        self.user_1 = G(User)
        self.user_2 = G(User)

        get_or_create_balance(self.user_1)
        get_or_create_balance(self.user_2)

        self.dotkom_grp = G(Group, name='dotKom')
        self.admin_grp = G(Group, name='feedmeadmin')

        Group.objects.get(name='dotKom').user_set.add(self.user_1)
        Group.objects.get(name='dotKom').user_set.add(self.user_2)
        Group.objects.get(name='feedmeadmin').user_set.add(self.user_2)

        self.restaurant = G(Restaurant)

        self.order_1 = G(Order)
        self.order_2 = G(Order)

        self.orderline_1 = G(OrderLine)
        self.orderline_2 = G(OrderLine)

    def test_join_multiple_orderlines_as_creator(self):
        user_1 = G(User)
        user_2 = G(User)

        order = G(Order)
        G(OrderLine, order=order, creator=user_1)
        G(OrderLine, order=order)

        self.assertTrue(in_other_orderline(user_1), 'User should be in another orderline')
        self.assertFalse(in_other_orderline(user_2), 'User should not be in another orderline')

    def test_join_multiple_orderlines_as_buddy(self):
        user_1 = G(User)
        user_2 = G(User)

        order = G(Order)
        G(OrderLine, order=order, users=[user_1])
        G(OrderLine, order=order)

        self.assertTrue(in_other_orderline(user_1), 'User should be in another orderline')
        self.assertFalse(in_other_orderline(user_2), 'User should not be in another orderline')
