from django.db import models
from django.contrib.auth.models import User, Group

from django.utils.translation import ugettext_lazy as _

class Order(models.Model):
    date = models.DateTimeField(_("dato"), auto_now_add=True, editable=False)
    total_sum = models.IntegerField(_("Sum"), max_length=4, default=0)

    def pizza_users(self):
        return Group.objects.get(name='pizza').user_set.all()

    def used_users(self):
        users = []
        for pizza in self.pizza_set.all():
            users.append(pizza.user)
            if pizza.buddy:
                users.append(pizza.buddy)
        return users

    def free_users(self):
        #Filters the used users from the list of users in the pizza group
        return [x for x in self.pizza_users() if x not in self.used_users()]
            

    class Meta:
        get_latest_by = 'date'
    
class Pizza(models.Model):
    order = models.ForeignKey(Order)
    user = models.ForeignKey(User, related_name="Owner")
    buddy = models.ForeignKey(User, related_name="Pizzabuddy", null=True)
    soda = models.CharField(_('brus'), blank=True, null=True, default='cola', max_length=25)
    dressing = models.BooleanField(_('hvitloksdressing'), default=True)
    pizza = models.IntegerField(_('pizzanummer'), max_length=2, default=8)

    def __init__(self, *args, **kwargs):
        super(Pizza, self).__init__(*args, **kwargs)
        self.order = Order.objects.all().latest()

    def __unicode__(self):
        return self.user.username
    
    @models.permalink
    def get_absolute_url(self):
        return ('edit', (), {'pizza_id' : self.id})

    class Meta:
        verbose_name = _('Pizza')
        verbose_name_plural = _('Pizzar')


class Saldo(models.Model):
    saldo = models.IntegerField(_('saldo'), max_length=5, default=0)
    user = models.ForeignKey(User, related_name="Saldomaster")





    
