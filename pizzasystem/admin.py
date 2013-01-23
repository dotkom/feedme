# -*- coding: utf-8 -*-

from django.contrib import admin
from models import PizzaSystem

class PizzaSystemAdmin(admin.ModelAdmin):
    list_display = ('user','soda','dressing','pizza')

admin.site.register(PizzaSystem, PizzaSystemAdmin)
