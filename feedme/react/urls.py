from django.conf.urls import patterns, include, url

from feedme.react.views import react_index


urlpatterns = (
    url(r'^$', react_index, name='react_index'),
)
