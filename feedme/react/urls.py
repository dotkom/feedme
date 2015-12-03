from django.conf.urls import patterns, include, url

from feedme.react import views


urlpatterns = (
    url(r'^$', views.index, name='react_index'),
    url(r'^(?P<group>\w+)/$', views.order, name='react_order'),
)
