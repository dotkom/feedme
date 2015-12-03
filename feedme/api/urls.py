from rest_framework import routers

from feedme.api.views import OrderViewSet, OrderLineViewSet


router = routers.SimpleRouter()
router.register('orders', OrderViewSet)
router.register('orderlines', OrderLineViewSet)

urlpatterns = router.urls
