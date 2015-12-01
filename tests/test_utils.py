from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import TestCase

from django_dynamic_fixture import G

from feedme.models import Order, OrderLine, Poll
from feedme.utils import get_order


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
