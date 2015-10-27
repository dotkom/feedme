from django.conf.urls import patterns, include, url


# react
from feedme.react_views import react_index
urlpatterns = (
    url(r'^$', react_index, name='react_index'),
)
