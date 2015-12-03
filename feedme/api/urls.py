from rest_framework import routers

from feedme.api.views import BalanceViewSet, OrderViewSet, OrderLineViewSet


router = routers.SimpleRouter()
router.register('balance', BalanceViewSet)
router.register('orders', OrderViewSet)
router.register('orderlines', OrderLineViewSet)

urlpatterns = router.urls
