from django.db import models
from django.contrib.auth.models import User, Group
from fields import PizzaMembersChoiceField

from django.utils.translation import ugettext_lazy as _

class Order(models.Model):
    date = models.DateTimeField(_("dato"), auto_now_add=True, editable=False)
    total_sum = models.IntegerField(_("Sum"), max_length=4, default=0)

    def pizza_users(self):
        return Group.objects.get(name='pizza').user_set.all()     

    class Meta:
        get_latest_by = 'date'
    
class Pizza(models.Model):
    # dynamisk hent ut folk fra gruppa som ikke er satt opp og lagre som choices
    #group = Group.objects.get(name='pizza')
    #users_in_group = group.user_set.all()
    order = models.ForeignKey(Order)
    user = models.ForeignKey(User, related_name="Owner")
    buddy = models.ForeignKey(User, related_name="Pizzabuddy", null=True)
    soda = models.CharField(_('brus'), blank=True, null=True, default='cola', max_length=25)
    dressing = models.BooleanField(_('hvitloksdressing'), default=True)
    pizza = models.IntegerField(_('pizzanummer'), max_length=2, default=8)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = _('Pizza')
        verbose_name_plural = _('Pizzar')

    
