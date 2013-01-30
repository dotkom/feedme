# -*- coding: utf-8 -*-

from django.contrib import admin
from models import Order, Pizza

class OrderAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sum')

admin.site.register(Order, OrderAdmin)
