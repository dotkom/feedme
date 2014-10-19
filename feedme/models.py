# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class Restaurant(models.Model):
    restaurant_name = models.CharField(_('name'), max_length=50)
    menu_url = models.URLField(_('menu url'), max_length=250)
    phone_number = models.CharField(_('phone number'), max_length=15)
    email = models.EmailField(_('email address'), blank=True, null=True)
    buddy_system = models.BooleanField(_('Enable buddy system'), default=False)

    def __unicode__(self):
        return self.restaurant_name

class Order(models.Model):
    date = models.DateField(_('date'))
    restaurant = models.ForeignKey(Restaurant)
    extra_costs = models.FloatField(_('extra costs'), default=0)
    active = models.BooleanField(_('Order currently active'), default=True)

    def get_total_sum(self):
        return self.orderline_set.aggregate(models.Sum(_('price')))

    def get_extra_costs(self):
        orderlines = self.orderline_set.all()
        users = 0
        for orderline in orderlines:
            if orderline.users:
                users += orderline.users.count()
            else:
                users += 1
        return self.extra_costs / users

    def order_users(self):
        return User.objects.filter(groups__name=settings.FEEDME_GROUP)

    def available_users(self):
        order_users = self.order_users()
        taken_users = self.taken_users()
        available_users = order_users.exclude(id__in=taken_users)
        return available_users

    def taken_users(self):
        return self.orderline_set.values_list(_('creator'), flat=True)

    def get_latest(self):
        if Order.objects.all():
                orders = Order.objects.all().order_by('-id')
                for order in orders:
                    if order.active:
                        return order
        else:
            return None

    def __init__(self):
        prev_active = self.get_latest()
        if prev_active != None:
            prev_active.active = False
            prev_active.save()

    def __unicode__(self):
        return "%s @ %s" % (self.date.strftime("%d-%m-%Y"), self.restaurant)

    class Meta:
        get_latest_by = 'date'

class OrderLine(models.Model):
    order = models.ForeignKey(Order)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name=_('owner'))
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name=_('buddies'), null=True, blank=True)
    menu_item = models.IntegerField(_('menu item'), max_length=2)
    soda = models.CharField(_('soda'), blank=True, null=True, max_length=25)
    extras = models.CharField(_('extras/comments'), blank=True, null=True, max_length=50)
    price = models.IntegerField(_('price'), max_length=4, default=100)
    paid_for = models.BooleanField(_('paid for'), default=False)

    def get_order(self):
        return self.order

    def get_buddies(self):
        return self.users

    def get_num_users(self):
        return len(self.users)

    def get_total_price(self):
        return (self.order.get_extra_costs() * self.users.count()) + self.price

    def __unicode__(self):
        if self.creator.username != "":
            return self.creator.username
        else:
            return self.creator.nickname

    @models.permalink
    def get_absolute_url(self):
        return ('edit', (), {'orderline_id' : self.id})

    class Meta:
        verbose_name = _('Order line')
        verbose_name_plural = _('Order lines')

class Balance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)
    balance = models.FloatField(_('balance'), default=0)

    def get_balance(self):
        return "%0.f kr" % self.balance

    def deposit(self, amount):
        if amount > 0:
            self.balance += amount
            return True
        else:
            return False # Error handling?

    def withdraw(self, amount):
        print self.balance
        if amount <= self.balance:
            self.balance -= amount
            return True
        else:
            return False

    def __unicode__(self):
        return "%s: %s" % (self.user, self.get_balance())

class ManageBalance(models.Model):
    user = models.ForeignKey(Balance)
    deposit = models.FloatField(_('deposit amount'), default=0)

class ManageOrders(models.Model):
    orders = models.OneToOneField(Order, related_name=_('Orders'))

class ManageUsers(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name=_('Users'))

class ManageOrderLimit(models.Model):
    order_limit = models.IntegerField(_('Order limit'), default=100)
