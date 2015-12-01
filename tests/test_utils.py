from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.test import TestCase

from datetime import date, datetime, timedelta

from django_dynamic_fixture import G, N

from feedme.models import Balance, Order, OrderLine, Poll
from feedme.utils import (
        get_next_tuesday, get_next_wednesday, get_or_create_balance, get_order,
        get_orderline_for_order_and_creator, get_poll, handle_deposit,
        manually_parse_users, pay, validate_users_funds
        )


class UtilsTestCase(TestCase):
    def setUp(self):
        pass

    def test_get_order_no_order_for_group(self):
        new_group = G(Group)
        self.assertEquals(None, get_order(new_group), "There should be no orders for a group with no orders")

    def test_get_order_group_with_active_order(self):
        group = G(Group)
        order = G(Order, group=group)

        self.assertEquals(order, get_order(group), "Got %s, expected %s." % (get_order(group), order))

    def test_get_order_group_with_inactive_order(self):
        group = G(Group)
        order = G(Order, group=group, active=False)

        self.assertEquals(None, get_order(group), "Got %s, expected %s." % (get_order(group), None))

    def test_get_poll_no_poll_for_group(self):
        new_group = G(Group)
        self.assertEquals(None, get_poll(new_group), "There should be no polls for a group with no polls")

    def test_get_order_group_with_active_order(self):
        group = G(Group)
        poll = G(Poll, group=group)

        self.assertEquals(poll, get_poll(group), "Got %s, expected %s." % (get_poll(group), poll))

    def test_get_order_group_with_inactive_order(self):
        group = G(Group)
        poll = G(Poll, group=group, active=False)

        self.assertEquals(None, get_poll(group), "Got %s, expected %s." % (get_poll(group), None))

    def test_handle_deposit(self):
        user = G(User)
        balance = G(Balance, user=user)

        initial_balance = 100
        positive_amount = 100
        negative_amount = -100
        balance.deposit(initial_balance)

        data = {'user': user, 'amount': positive_amount}
        handle_deposit(data)
        self.assertEquals((initial_balance + positive_amount), balance.get_balance(), "Got %s, expected %s." % (balance.get_balance(), (initial_balance + positive_amount)))

        data = {'user': user, 'amount': negative_amount}
        handle_deposit(data)
        should_be = (initial_balance + positive_amount - negative_amount)
        self.assertEquals(should_be, balance.get_balance(), "Got %s, expected %s." % (balance.get_balance(), should_be))

    def test_pay(self):
        user = G(User)
        balance = G(Balance, user=user)
        amount = 100
        initial_balance = 250
        balance.deposit(initial_balance)

        pay(user, amount)
        self.assertEquals((initial_balance - amount), balance.get_balance(), "Got %s, expected %s" % (balance.get_balance(), (initial_balance - amount)))

    def test_get_next_tuesday(self):
        d = date.today()
        days_ahead = 1 - d.weekday()  # Monday 0, Tuesday 1, ...
        if days_ahead < 0:  # Has already happened, use <= if include today too
            days_ahead += 7
        next_tuesday = d + timedelta(days=days_ahead)

        self.assertEquals(next_tuesday, get_next_tuesday(), "Got %s, expected %s" % (get_next_tuesday(), next_tuesday))

    def test_get_next_wednesday(self):
        d = date.today()
        days_ahead = 2 - d.weekday()  # Monday 0, Tuesday 1, ...
        if days_ahead < 0:  # Has already happened, use <= if include today too
            days_ahead += 7
        next_wednesday = d + timedelta(days=days_ahead)

        self.assertEquals(next_wednesday, get_next_wednesday(), "Got %s, expected %s" % (get_next_wednesday(), next_wednesday))

    def test_manually_parse_users_noone(self):
        list_of_available_users = """<form><select><option value="1">Testbruker</option><option value="2">Testbruker Valgt</option></select>"""
        chosen_users = []
        self.assertEquals(chosen_users, manually_parse_users(list_of_available_users), "Got %s, expected %s" % (manually_parse_users(list_of_available_users), chosen_users))

    def test_manually_parse_users_one(self):
        chosen_user = G(User, id=2)
        list_of_available_users = """<form><select><option value="1">Testbruker</option><option value="2" selected>Testbruker Valgt</option></select>"""
        chosen_users = [chosen_user]
        self.assertEquals(chosen_users, manually_parse_users(list_of_available_users),
                "Got %s, expected %s" % \
                        (manually_parse_users(list_of_available_users), chosen_users))

    def test_get_ol_for_ol_and_creator(self):
        creator = G(User)
        not_creator = G(User)
        order = G(Order)
        orderline = G(OrderLine, order=order, creator=creator)
        not_saved_ol = N(OrderLine, order=order, creator=creator)

        fake_ol = get_orderline_for_order_and_creator(order, not_creator)

        self.assertEquals(True, fake_ol[1], "Got %s, expected %s" % (fake_ol[1], True))

        correct_ol = get_orderline_for_order_and_creator(order, creator)
        self.assertEquals(orderline, correct_ol[0], "Got %s, expected %s" % (correct_ol, orderline))

    def test_validate_users_funds_one_unsufficient(self):
        user_sufficient = G(User)
        user_unsufficient = G(User)

        get_or_create_balance(user_sufficient).deposit(50)

        unsufficient_funds_users = validate_users_funds([user_sufficient, user_unsufficient], 25)
        self.assertEquals([user_unsufficient], unsufficient_funds_users,
                "Got %s, expected %s." % (unsufficient_funds_users, [user_unsufficient]))

