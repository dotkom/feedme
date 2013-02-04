from django.conf.urls import patterns, include, url

urlpatterns = patterns('pizzasystem.views',
    url(r'^$', 'index', name='pizza_index'),
    url(r'^newpizza', 'newpizza', name='new_pizza'),
    url(r'^add', 'add', name='add_pizza'),
    url(r'^(?P<pizza_id>\d+)/$','edit', name='edit'),
    url(r'^edit', 'edit_function', name='edit_function'),
)
