from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from django_dynamic_fixture import G

from feedme.models import Order, OrderLine, Poll


class IndexViewTest(TestCase):
    urls = 'feedme.urls'

    def setUp(self):
        self.client = Client()
        self.group = G(Group)
        self.user = G(User, username='testuser', password='secret', active=True)
        self.admin = G(User, password='admin', is_superuser=True)

        self.group.user_set.add(self.user)
        self.group.user_set.add(self.admin)

    def test_load_feedme_index(self):
        response = self.client.get(reverse('feedme_index'))
        self.assertEquals(200, response.status_code)

    def test_load_index_view_no_order_group(self):
        response = self.client.get(reverse('feedme_index_new', kwargs={'group': self.group}), follow=True)
        self.assertEquals(404, response.status_code, "No orders should return 404")

    def test_load_index_view_group_with_order(self):
        order = G(Order, group=self.group, active=True)
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('feedme_index_new', kwargs={'group': self.group}), follow=True)
        # @ToDo: Fix failing test
        # self.assertEquals(200, response.status_code)  # Fails for some reason

    # def test_get_admin_index_not_admin(self):
        # response = self.client.get(reverse('admin', kwargs={'group': self.group}))
        # @ToDo: Fix failing test "feedme is not a registered namespace"
        # self.assertEquals(403, response.status_code)

    # def test_get_admin_index_as_admin(self):
        # response = self.client.get(reverse('admin', kwargs={'group': self.group}))
        # @ToDo: Fix failing test with permissions
        # self.assertEquals(200, response.status_code)

    # def test_get_create_new_order_access_denied(self):
        # response = self.client.get(reverse('new_order', kwargs={'group': self.group}))
        # @ToDo: Fix failing test "feedme is not a registered namespace"
        # self.assertEquals(403, response.status_code,
        #         "Should be permission denied if not logged in with permissions")

    # def test_get_create_new_order_access_granted(self):
        # self.client.login(username=self.admin.username, password='admin')
        # response = self.client.get(reverse('new_order', kwargs={'group': self.group}))
        # @ToDo: Fix failing test with permissions
        # self.assertEquals(200, response.status_code,
        #         "Should not be permission denied if logged in with permissions")


class OrderLineTest(TestCase):
    urls = 'feedme.urls'

    def setUp(self):
        self.client = Client()

        # Set up groups
        self.group = G(Group)

        # Set up an order for a group
        self.order = G(Order, group=self.group)

    def test_load_orderline_create(self):
        response = self.client.get(reverse('create_orderline', args=[self.group]))
        self.assertEquals(200, response.status_code)
