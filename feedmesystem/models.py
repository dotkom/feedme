# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import Group
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
#from django.contrib.auth import get_user_model

User = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')

class Order(models.Model):
    date = models.DateField(_("dato"))
    total_sum = models.IntegerField(_("Sum"), max_length=4, default=0)
    # ?
    #order_line = models.ForeignKey(OrderLine)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField(_(u'beskrivelse'))
    # ?

    def order_users(self):
        return User.objects.filter(groups__name=settings.FEEDME_GROUP)

    def used_users(self):
        users = []
        for order in self.order_set.all():
            users.append(order.user)
            if order.buddy:
                users.append(order.buddy)
        return users

    def free_users(self, buddy=None, orderuser=None):
        free_users = self.order_users()
        for user in self.used_users():
            if not (user == buddy or user == orderuser):
                free_users = free_users.exclude(id=user.id)
        return free_users

    def __unicode__(self):
        return self.date.strftime("%d-%m-%Y")

    class Meta:
        get_latest_by = 'date'

class OrderLine(models.Model):
    order = models.ForeignKey(Order)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="Owner")
    need_buddy = models.BooleanField(_('Trenger Buddy'), default=False)
    buddy = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="Orderbuddy", null=True, blank=True)
    soda = models.CharField(_('brus'), blank=True, null=True, default='cola', max_length=25)
    dressing = models.BooleanField(_(u'hvitløksdressing'), default=True)
    menu_item = models.IntegerField(_('menynummer'), max_length=2, default=8)

    def __unicode__(self):
        return self.user.username

    @models.permalink
    def get_absolute_url(self):
        return ('edit', (), {'orderline_id' : self.id})

    class Meta:
        verbose_name = _('Ordre')
        verbose_name_plural = _('Ordre')

"""class Order(models.Model):
    order_line = models.ForeignKey(OrderLine)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField(_(u'beskrivelse'))

    def __unicode__(self):
        return self.user.username
""" # @TODO Scratch this

class Saldo(models.Model):
    saldo = models.FloatField(_('saldo'), default=0)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

class ManageOrderLines(models.Model):
    order_lines = models.OneToOneField(OrderLine, related_name=_('Ordre'))
    total_sum = models.IntegerField(_('Total regning'), max_length=4)

class ManageUsers(models.Model):
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name=_('Brukere'))
    #users.help_text = ''
    add_value = models.IntegerField(_('Verdi'), max_length=4)
    add_value.help_text = _(u'Legger til verdien på alle valgte brukere')


class ManageOrderLimit(models.Model):
    order_limit = models.IntegerField(_('Bestillings grense'), default=100)
