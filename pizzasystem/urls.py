from django.conf.urls import patterns, include, url

urlpatterns = patterns('pizzasystem.views',
    url(r'^$', 'index', name='pizza_index'),
    url(r'^pizzaview/$', 'pizzaview', name='newpizza'),
    url(r'^pizzaview/other/$', 'otherview', name='newother'),
    url(r'^edit/(?P<pizza_id>\d+)/$','edit', name='edit'),
    url(r'^delete/(?P<pizza_id>\d+)/$','delete', name='delete'),
    url(r'^join/(?P<pizza_id>\d+)/$','join', name='join'),
    url(r'^admin/$', 'new_order', name='admin'),
    url(r'^admin/neworder/$', 'new_order', name='new_order'),
    url(r'^admin/orders/$', 'orders', name='orders'),
    url(r'^admin/users/$', 'users', name='users'),
    url(r'^admin/orderlimit/$', 'order_limit', name='order_limit'),
)
