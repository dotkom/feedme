from datetime import date

from django.test import TestCase

from django_dynamic_fixture import G

from django.contrib.auth.models import User, Group
from feedme.models import Order, OrderLine, Restaurant, Balance
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

    def test_create_user_balance(self):
        feedme_user = User.objects.get(username='FeedmeUser1')
        feedme_user_balance = get_or_create_balance(feedme_user)

        self.assertEqual(feedme_user_balance.get_balance(), '0 kr', 'Balance should be \'0 kr\' when creating a new balance object')

    def test_deposit_and_withdraw(self):
        feedme_user = User.objects.get(username='FeedmeUser1')
        feedme_user = get_or_create_balance(feedme_user)

        self.assertEqual(feedme_user.balance, 0, 'Balance should be 0 when creating a new balance object')
        self.assertEqual(feedme_user.deposit(50), True, 'Should return True for depositing with success')
        self.assertEqual(feedme_user.balance, 50, 'Balance should be 50 after depositing 50')
        self.assertEqual(feedme_user.deposit(-50), False, 'Should return False for depositing negative amount')
        self.assertEqual(feedme_user.balance, 50, 'Balance should be 50 after trying to deposit -50')
        self.assertEqual(feedme_user.withdraw(25), True, 'Should return True for withdrawing an amount you can afford')
        self.assertEqual(feedme_user.balance, 25, 'Balance should be 25 after withdrawing 25')
        self.assertEqual(feedme_user.withdraw(50), False, 'Should return False, but still allow dotKommers to overload their balance')
        self.assertEqual(feedme_user.balance, -25, 'Someone overloaded their account')

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

    def user_able_to_see_index(self):
        regular_user = User.objects.get(username='TestUser1')
        feedme_user = User.objects.get(username='FeedmeUser1')
        admin_user = User.objects.get(username='AdminUser1')

        self.assertEqual(1,1)
        # @ToDo

class ViewMoneyLogicTestCase(TestCase):
    def test_validate_user_funds(self):
        feedme_user = G(User)
        feedme_user_balance = get_or_create_balance(feedme_user)

        feedme_user.balance.deposit(100)
        feedme_user.balance.save()

        self.assertTrue(validate_user_funds(feedme_user, 99), 'Expected %s, but got %s\nShould evaluate to True when user.balance >= funds.' % (True, validate_user_funds(feedme_user, 99)))
        self.assertTrue(validate_user_funds(feedme_user, 100), 'Should evaluate to True when user.balance >= funds.')
        self.assertFalse(validate_user_funds(feedme_user, 101), 'User does not have enough funds')

class ViewLogicTestCase(TestCase):
    def set_up(self):
        self.user_1 = G(User)
        self.user_2 = G(User)

        get_or_create_balance(user_1)
        get_or_create_balance(user_2)

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
        orderline_1 = G(OrderLine, order=order, creator=user_1)
        orderline_2 = G(OrderLine, order=order)

        self.assertTrue(in_other_orderline(user_1), 'User should be in another orderline')
        self.assertFalse(in_other_orderline(user_2), 'User should not be in another orderline')

    def test_join_multiple_orderlines_as_buddy(self):
        user_1 = G(User)
        user_2 = G(User)

        order = G(Order)
        orderline_1 = G(OrderLine, order=order, users=[user_1])
        orderline_2 = G(OrderLine, order=order)

        self.assertTrue(in_other_orderline(user_1), 'User should be in another orderline')
        self.assertFalse(in_other_orderline(user_2), 'User should not be in another orderline')
