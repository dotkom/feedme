from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import permission_required

from feedme.views import OrderlineDetail, ManageUserViewSet

# API
from tastypie.api import Api
from feedme.api import PollResource, RestaurantResource, VoteResource, OrderResource, OrderLineResource

v1_api = Api(api_name='v1')
v1_api.register(PollResource())
v1_api.register(RestaurantResource())
v1_api.register(VoteResource())
v1_api.register(OrderResource())
v1_api.register(OrderLineResource())

urlpatterns = patterns(
    'feedme.views',
    url(r'^$', 'index', name='feedme_index'),

    # Enabled
    url(r'^neworder/$', 'orderlineview', name='new_orderline'),
    url(r'^edit/(?P<orderline_id>\d+)/$', 'edit_orderline', name='edit_orderline'),
    url(r'^delete/(?P<orderline_id>\d+)/$', 'delete_orderline', name='delete_orderline'),
    url(r'^order/$', 'orderview', name='new_order'),

    # Disabled
    # url(r'^order/(?P<order_id>\d+)/$', 'edit_order', name='edit_order'),
    # url(r'^delete/order/(?P<order_id>\d+)/$','delete_order', name='delete_order'),

    # Enabled
    url(r'^join/(?P<orderline_id>\d+)/$', 'join_orderline', name='join_orderline'),
    url(r'^leave/(?P<orderline_id>\d+)/$', 'leave_orderline', name='leave_orderline'),

    # Admin (enabled)
    url(r'^admin/$', 'new_order', name='feedme_admin'),
    url(r'^admin/neworder/$', 'new_order', name='new_order'),
    url(r'^admin/orders/$', 'manage_order', name='manage_order'),
    # url(r'^admin/users/$', 'manage_users', name='manage_users'),
    url(r'^admin/newrestaurant/$', 'new_restaurant', name='new_restaurant'),
    url(r'^admin/newpoll/$', 'new_poll', name='new_poll'),

    url(r'^history/$', 'order_history', name='feedme_order_history'),

    # New
    url(r'^(?P<group>\w+)/$', 'index_new', name='feedme_index_new'),
    url(r'^(?P<group>\w+)/create/$', 'create_orderline', name='create_orderline'),
    url(r'^(?P<group>\w+)/edit/(?P<orderline_id>\d+)/$', 'edit_orderline', name='edit_orderline'),
    url(r'^(?P<group>\w+)/delete/(?P<orderline_id>\d+)/$', 'delete_orderline', name='delete_orderline'),
    url(r'^(?P<group>\w+)/join/(?P<orderline_id>\d+)/$', 'join_orderline', name='join_orderline'),
    url(r'^(?P<group>\w+)/leave/(?P<orderline_id>\d+)/$', 'leave_orderline', name='leave_orderline'),


    # New admin
    url(r'^(?P<group>\w+)/admin/$', 'admin', name='admin'),
    url(r'^(?P<group>\w+)/admin/neworder/$', 'new_order', name='new_order'),
    url(r'^(?P<group>\w+)/admin/orders/$', 'manage_order', name='manage_order'),
    url(r'^(?P<group>\w+)/admin/users/$', permission_required('feedme.add_balance')(ManageUserViewSet.as_view()), name='manage_users'),
    url(r'^(?P<group>\w+)/admin/newrestaurant/$', 'new_restaurant', name='new_restaurant'),
    url(r'^(?P<group>\w+)/admin/newpoll/$', 'new_poll', name='new_poll'),

    # Api
    url(r'api/', include(v1_api.urls)),
)
