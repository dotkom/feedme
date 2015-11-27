# coding=utf-8

from datetime import date, timedelta

import django
django.setup()
from django.test import TestCase

from django.contrib.auth.models import User, Group
from feedme.models import Order, OrderLine, Restaurant, Balance, Transaction, Poll, Answer
from feedme.utils import validate_user_funds, in_other_orderline, get_or_create_balance


class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='TestUser1')
        self.user2 = User.objects.create(username='FeedmeUser1')
        self.user3 = User.objects.create(username='AdminUser1')

        self.group = Group.objects.create(name='dotKom')
        self.group1 = Group.objects.create(name='feedmeadmin')

        Group.objects.get(name='dotKom').user_set.add(User.objects.get(username='FeedmeUser1'))
        Group.objects.get(name='dotKom').user_set.add(User.objects.get(username='AdminUser1'))
        Group.objects.get(name='feedmeadmin').user_set.add(User.objects.get(username='AdminUser1'))

        self.restaurant = Restaurant.objects.create(restaurant_name="Testaurant")

        self.order = Order.objects.create(
            group=self.group,
            restaurant=self.restaurant,
            date=date.today(),
            extra_costs=0,
            active=True,
            use_validation=False
        )

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


class OrderTestCase(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='dotKom')

        self.user = User.objects.create(username='TestUser1')
        self.user2 = User.objects.create(username='FeedmeUser1')
        self.user3 = User.objects.create(username='AdminUser1')
        self.user4 = User.objects.create(username='AdminUser2')

        self.restaurant = Restaurant.objects.create(restaurant_name="Testaurant")

        self.order = Order.objects.create(
            group=self.group,
            restaurant=self.restaurant,
            date=date.today(),
            extra_costs=0,
            active=True,
            use_validation=False
        )

        self.orderline = OrderLine.objects.create(
            order=self.order,
            creator=self.user,
            menu_item="",
            soda="",
            extras="",
            price=100,
            paid_for=False
        )

        self.orderline2 = OrderLine.objects.create(
            order=self.order,
            creator=self.user2,
            menu_item="",
            soda="",
            extras="",
            price=100,
            paid_for=False
        )

    def test_get_total_sum(self):
        order_1 = self.order
        orderline_1 = self.orderline
        orderline_2 = self.orderline2

        s = orderline_1.price + orderline_2.price + order_1.extra_costs
        r = order_1.get_total_sum
        self.assertEqual(r, s, 'Got %s, expected %s' % (r, s))

        order2 = Order.objects.create(
            group=self.group,
            restaurant=self.restaurant,
            date=date.today(),
            extra_costs=0,
            active=True,
            use_validation=False
        )
        orderline_3 = OrderLine.objects.create(
            order=order2,
            creator=self.user2,
            menu_item="",
            soda="",
            extras="",
            price=100,
            paid_for=False
        )
        orderline_4 = OrderLine.objects.create(
            order=order2,
            creator=self.user2,
            menu_item="",
            soda="",
            extras="",
            price=100,
            paid_for=False
        )

        s = orderline_3.price + orderline_4.price + order2.extra_costs
        r = order2.get_total_sum
        self.assertEqual(r, s, 'Got %s, expected %s' % (r, s))

    def get_total_sum_with_extra_costs(self):
        self.order.extra_costs=50
        self.user = self.user
        self.user2 = self.user2
        user_3 = self.user3
        orderline_1 = OrderLine.objects.create(order=self.order, price=25)
        orderline_1.users.add(self.user)
        orderline_1.users.add(self.user2)
        orderline_2 = OrderLine.objects.create(order=self.order, price=25)
        orderline_2.users.add(user_3)
        self.assertEqual(self.order.get_total_sum, 100)

    def get_price_per_user(self):
        self.order.extra_costs = 50
        self.user = self.user
        self.user2 = self.user
        user_3 = self.user
        user_4 = self.user
        orderline_1 = OrderLine.objects.create(order=self.order, price=25)
        orderline_1.users.add(self.user)
        orderline_1.users.add(self.user2)
        orderline_2 = OrderLine.objects.create(order=self.order, price=25)
        orderline_2.users.add(user_3)
        self.assertEqual(orderline_1.get_price_to_pay(), 25,
                         'expected %s, got %s'% ('25', orderline_1.get_price_to_pay()))

    def test_get_extra_costs_one_user(self):
        self.order.extra_costs = 50
        self.orderline.order = self.order
        self.orderline.creator = self.user
        self.orderline.users = [self.user,]
        self.assertEqual(self.order.get_extra_costs(), 50)

    def test_get_extra_costs_two_users_one_orderline(self):
        self.order.extra_costs = 50
        self.orderline.order = self.order
        self.orderline.creator = self.user
        self.orderline.users = [self.user, self.user2]
        self.assertEqual(self.order.get_extra_costs(), 25)

    def test_get_extra_costs_two_users_two_orderlines(self):
        self.order.extra_costs = 50
        self.orderline.users = [self.user]
        self.orderline2.users = [self.user3]
        self.assertEqual(self.order.get_extra_costs(), 25)

    def test_get_extra_costs_one_user_two_orderlines(self):
        self.order.extra_costs = 50
        self.orderline.users = [self.user]
        self.orderline2.users = [self.user]
        self.assertEqual(self.order.get_extra_costs(), 25)

    def test_get_extra_costs_two_orderlines_three_users(self):
        self.order.extra_costs = 75
        self.orderline.users = [self.user, self.user2]
        self.orderline2.users = [self.user3]
        self.assertEqual(self.order.get_extra_costs(), 25)

    def test_get_latest(self):
        self.order.date = date.today() - timedelta(days=1)
        Order.objects.create(
            group=self.group,
            restaurant=self.restaurant,
            date=date.today(),
            extra_costs=0,
            active=False,
            use_validation=False
        )
        self.assertEqual(self.order.get_latest(), self.order)
        self.order.active = False
        self.order.save()
        self.assertFalse(self.order.get_latest())


class OrderLineTestCase(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='dotKom')

        self.user = User.objects.create(username='TestUser1')
        self.user2 = User.objects.create(username='FeedmeUser1')
        self.user3 = User.objects.create(username='AdminUser1')
        self.user4 = User.objects.create(username='AdminUser2')

        self.restaurant = Restaurant.objects.create(restaurant_name="Testaurant")

        self.order = Order.objects.create(
            group=self.group,
            restaurant=self.restaurant,
            date=date.today(),
            extra_costs=0,
            active=True,
            use_validation=False
        )

        self.orderline = OrderLine.objects.create(
            order=self.order,
            creator=self.user,
            menu_item="",
            soda="",
            extras="",
            price=100,
            paid_for=False
        )
        self.orderline.users.add(self.user)

        self.orderline2 = OrderLine.objects.create(
            order=self.order,
            creator=self.user,
            menu_item="",
            soda="",
            extras="",
            price=100,
            paid_for=False
        )
        self.orderline2.users.add(self.user2)

    def test_get_order(self):
        self.assertEqual(self.order.get_latest(), self.order)

    def test_num_users(self):
        self.orderline.users = [self.user]
        self.assertEquals(self.orderline.get_num_users(), 1)

        self.orderline.users.add(self.user2)
        self.assertEquals(self.orderline.get_num_users(), 2)

    def test_get_total_price(self):
        self.order.price=100
        self.orderline.users.add(self.user)

        self.assertEquals(self.orderline.get_total_price(), 100)

    def test_get_price_to_pay(self):
        self.orderline.price = 100
        self.orderline.users = [self.user]
        self.assertEquals(self.orderline.get_price_to_pay(), 100)

        self.orderline.users.add(self.user2)
        self.assertEquals(self.orderline.get_price_to_pay(), 50)

    def test_get_price_to_pay_two_users_one_orderline(self):
        order = Order.objects.create(
            group=self.group,
            restaurant=self.restaurant,
            date=date.today(),
            extra_costs=50,
            active=True,
            use_validation=False
        )
        self.orderline.order = order
        self.orderline.price = 100
        self.orderline.users = [self.user, self.user2]
        self.orderline.save()
        self.assertEqual(self.orderline.get_price_to_pay(), 75)

    def test_get_price_to_pay_two_users_two_orderlines(self):
        self.order.extra_costs = 50
        self.assertEqual(self.orderline.get_price_to_pay(), 125)
        self.assertEqual(self.orderline2.get_price_to_pay(), 125)

    def test_get_price_to_pay_three_users_two_orderlines(self):
        self.order.extra_costs = 75
        self.orderline.users = [self.user, self.user2]
        self.orderline.price = 100
        self.orderline2.users = [self.user3]
        self.orderline2.price = 100
        self.assertEqual(self.orderline.get_price_to_pay(), 75)
        self.assertEqual(self.orderline2.get_price_to_pay(), 125)


class TransactionTestCase(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='dotKom')

        self.user = User.objects.create(username='TestUser1')
        self.user2 = User.objects.create(username='FeedmeUser1')
        self.user3 = User.objects.create(username='AdminUser1')
        self.user4 = User.objects.create(username='AdminUser2')

        self.restaurant = Restaurant.objects.create(restaurant_name="Testaurant")

        self.order = Order.objects.create(
            group=self.group,
            restaurant=self.restaurant,
            date=date.today(),
            extra_costs=0,
            active=True,
            use_validation=False
        )

        self.orderline = OrderLine.objects.create(
            order=self.order,
            creator=self.user,
            menu_item="",
            soda="",
            extras="",
            price=100,
            paid_for=False
        )

        self.balance = Balance.objects.create(user=self.user)

    def test_get_user_balance(self):
        balance = Balance.objects.get(user=self.user)
        goc_balance = get_or_create_balance(self.user)
        self.assertEquals(self.user, balance.user, 'User should match balance.user')
        self.assertEquals(self.user, goc_balance.user, 'User should match balance_user from get_or_create()')

    def test_transactions(self):
        get_or_create_balance(self.user)

        Transaction.objects.create(user=self.user, amount=100.0)
        self.assertTrue(self.user.balance.get_balance(), 100.0)

        Transaction.objects.create(user=self.user, amount=-100.0)
        self.assertEqual(self.user.balance.get_balance(), 0.0)
        self.assertEqual(self.user.transaction_set.count(), 2)

    def test_negative_transactions(self):
        # It is expected that people CAN go below zero!
        get_or_create_balance(self.user)

        Transaction.objects.create(user=self.user, amount=-1)
        self.assertEqual(self.user.balance.get_balance(), -1.0)

    def test_balance_deposit(self):
        get_or_create_balance(self.user)

        self.assertTrue(self.user.balance.deposit(100))
        self.assertEqual(self.user.balance.get_balance(), 100)
        self.assertTrue(self.user.balance.deposit(-50))
        self.assertEqual(self.user.balance.get_balance(), 50)
        self.assertTrue(self.user.balance.withdraw(50))
        self.assertEqual(self.user.balance.get_balance(), 0)

    def test_transaction_validation_on_validation_disabled(self):
        get_or_create_balance(self.user)

        self.assertEqual(self.user.balance.get_balance(), 0)
        self.assertTrue(self.user, 100)


class ViewMoneyLogicTestCase(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='dotKom')

        self.user = User.objects.create(username='TestUser1')
        self.user2 = User.objects.create(username='FeedmeUser1')
        self.user3 = User.objects.create(username='AdminUser1')
        self.user4 = User.objects.create(username='AdminUser2')

        self.restaurant = Restaurant.objects.create(restaurant_name="Testaurant")

        self.order = Order.objects.create(
            group=self.group,
            restaurant=self.restaurant,
            date=date.today(),
            extra_costs=0,
            active=True,
            use_validation=False
        )

        self.orderline = OrderLine.objects.create(
            order=self.order,
            creator=self.user,
            menu_item="",
            soda="",
            extras="",
            price=100,
            paid_for=False
        )

    def test_validate_user_funds(self):
        get_or_create_balance(self.user)

        self.user.balance.deposit(100)
        self.user.balance.save()

        self.assertTrue(validate_user_funds(self.user, 99),
                        'Should evaluate to True when user.balance >= funds.')
        self.assertTrue(validate_user_funds(self.user, 100),
                        'Should evaluate to True when user.balance >= funds.')
        self.assertFalse(validate_user_funds(self.user, 101),
                         'User does not have enough funds')


class ViewLogicTestCase(TestCase):
    def setUp(self):
        self.group = Group.objects.create(name='dotKom')

        self.user = User.objects.create(username='TestUser1')
        self.user2 = User.objects.create(username='FeedmeUser1')
        self.user3 = User.objects.create(username='AdminUser1')
        self.user4 = User.objects.create(username='AdminUser2')

        self.restaurant = Restaurant.objects.create(restaurant_name="Testaurant")

        self.order = Order.objects.create(
            group=self.group,
            restaurant=self.restaurant,
            date=date.today(),
            extra_costs=0,
            active=True,
            use_validation=False
        )

        self.orderline = OrderLine.objects.create(
            order=self.order,
            creator=self.user,
            menu_item="",
            soda="",
            extras="",
            price=100,
            paid_for=False
        )

        self.orderline2 = OrderLine.objects.create(
            order=self.order,
            creator=self.user2,
            menu_item="",
            soda="",
            extras="",
            price=100,
            paid_for=False
        )

    def test_join_multiple_orderlines_as_creator(self):
        self.order.group = self.group

        self.assertTrue(in_other_orderline(self.order, self.user), 'User should be in another orderline')
        self.assertFalse(in_other_orderline(self.order, self.user3), 'User should not be in another orderline')

    def test_join_multiple_orderlines_as_buddy(self):
        self.order.group = self.group

        self.assertTrue(in_other_orderline(self.order, self.user), 'User should be in another orderline')
        self.assertFalse(in_other_orderline(self.order, self.user3), 'User should not be in another orderline')
