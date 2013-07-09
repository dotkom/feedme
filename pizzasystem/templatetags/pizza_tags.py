# -*- coding: utf-8 -*-

from django import template

register = template.Library()

@register.inclusion_tag('pizza_tabs.html')
def pizza_tabs(active):
    return {'active': active}
