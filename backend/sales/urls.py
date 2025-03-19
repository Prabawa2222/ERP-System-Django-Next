from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, SaleViewSet, SaleItemViewSet

router = DefaultRouter()
router.register("customers", CustomerViewSet)
router.register("sales", SaleViewSet)
router.register("items", SaleItemViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
