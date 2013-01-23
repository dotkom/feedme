from django.db import models
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _

class PizzaSystem(models.Model):
    # dynamisk hent ut folk fra gruppa som ikke er satt opp og lagre som choices
    user = models.ForeignKey(User, related_name=_('bestiller'), null=True)
#    buddy = ChoiceField('pizzabuddy', choices=CHOICES)
    soda = models.CharField(_('brus'), blank=True, null=True, default='cola', max_length=25)
    dressing = models.BooleanField(_('hvitloksdressing'), default=True)
    pizza = models.IntegerField(_('pizzanummer'), max_length=2, default=8)
    
    def __unicode__(self):
        return "Pizza bestilling"

    class Meta:
        verbose_name = _('Pizza')
        verbose_name_plural = _('Pizzzzas')
    
