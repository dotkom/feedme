from django.conf.urls import url
from django.contrib.auth.decorators import permission_required

from feedme import views as feedme_views
from feedme.views import ManageUserViewSet


urlpatterns = [
    url(r'^$', feedme_views.index, name='feedme_index'),

    # Enabled
    url(r'^neworder/$', feedme_views.orderlineview, name='new_orderline'),
    url(r'^edit/(?P<orderline_id>\d+)/$', feedme_views.edit_orderline, name='edit_orderline'),
    url(r'^delete/(?P<orderline_id>\d+)/$', feedme_views.delete_orderline, name='delete_orderline'),
    url(r'^order/$', feedme_views.orderview, name='new_order'),

    # Disabled
    # url(r'^order/(?P<order_id>\d+)/$', 'edit_order', name='edit_order'),
    # url(r'^delete/order/(?P<order_id>\d+)/$','delete_order', name='delete_order'),

    # Enabled
    url(r'^join/(?P<orderline_id>\d+)/$', feedme_views.join_orderline, name='join_orderline'),
    url(r'^leave/(?P<orderline_id>\d+)/$', feedme_views.leave_orderline, name='leave_orderline'),

    # Admin (enabled)
    url(r'^admin/$', feedme_views.new_order, name='feedme_admin'),
    url(r'^admin/neworder/$', feedme_views.new_order, name='new_order'),
    url(r'^admin/orders/$', feedme_views.manage_order, name='manage_order'),
    # url(r'^admin/users/$', 'manage_users', name='manage_users'),
    url(r'^admin/newrestaurant/$', feedme_views.new_restaurant, name='new_restaurant'),
    url(r'^admin/newpoll/$', feedme_views.new_poll, name='new_poll'),

    url(r'^history/$', feedme_views.order_history, name='feedme_order_history'),

    # New
    url(r'^(?P<group>\w+)/$', feedme_views.index_new, name='feedme_index_new'),
    url(r'^(?P<group>\w+)/create/$', feedme_views.create_orderline, name='create_orderline'),
    url(r'^(?P<group>\w+)/edit/(?P<orderline_id>\d+)/$', feedme_views.edit_orderline, name='edit_orderline'),
    url(r'^(?P<group>\w+)/delete/(?P<orderline_id>\d+)/$', feedme_views.delete_orderline, name='delete_orderline'),
    url(r'^(?P<group>\w+)/join/(?P<orderline_id>\d+)/$', feedme_views.join_orderline, name='join_orderline'),
    url(r'^(?P<group>\w+)/leave/(?P<orderline_id>\d+)/$', feedme_views.leave_orderline, name='leave_orderline'),


    # New admin
    url(r'^(?P<group>\w+)/admin/$', feedme_views.admin, name='admin'),
    url(r'^(?P<group>\w+)/admin/neworder/$', feedme_views.new_order, name='new_order'),
    url(r'^(?P<group>\w+)/admin/orders/$', feedme_views.manage_order, name='manage_order'),
    url(r'^(?P<group>\w+)/admin/users/$', permission_required('feedme.add_balance')(ManageUserViewSet.as_view()),
        name='manage_users'),
    url(r'^(?P<group>\w+)/admin/newrestaurant/$', feedme_views.new_restaurant, name='new_restaurant'),
    url(r'^(?P<group>\w+)/admin/newpoll/$', feedme_views.new_poll, name='new_poll'),
]
