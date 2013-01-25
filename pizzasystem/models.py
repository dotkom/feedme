from django.db import models
from django.contrib.auth.models import User, Group
from fields import PizzaMembersChoiceField

from django.utils.translation import ugettext_lazy as _

class PizzaSystem(models.Model):
    # dynamisk hent ut folk fra gruppa som ikke er satt opp og lagre som choices
    group = Group.objects.get(name='pizza')
    users_in_group = group.user_set.all()
    user = models.ForeignKey(User, related_name=_('bestiller'), null=True)
    buddy = PizzaMembersChoiceField(queryset=users_in_group)
    soda = models.CharField(_('brus'), blank=True, null=True, default='cola', max_length=25)
    dressing = models.BooleanField(_('hvitloksdressing'), default=True)
    pizza = models.IntegerField(_('pizzanummer'), max_length=2, default=8)
    
    def __unicode__(self):
        return "Pizza bestilling"

    class Meta:
        verbose_name = _('Pizza')
        verbose_name_plural = _('Pizzzzas')

    
