from django.contrib.auth.models import Group
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from django_dynamic_fixture import G

from feedme.models import Order, OrderLine, Poll


class IndexViewTest(TestCase):
    urls = 'feedme.urls'

    def setUp(self):
        self.client = Client()

    def test_load_index_view(self):
        response = self.client.get(reverse('feedme_index'))
        self.assertEquals(200, response.status_code)


class OrderLineTest(TestCase):
    urls = 'feedme.urls'

    def setUp(self):
        self.client = Client()

        # Set up groups
        self.group = Group.objects.create(name='testgroup')

        # Set up an order for a group
        self.order = G(Order, group=self.group)

    def test_load_orderline_create(self):
        response = self.client.get(reverse('create_orderline', args=[self.group]))
        self.assertEquals(200, response.status_code)
