from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ProductViewSet, StockMovementViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet)
router.register("products", ProductViewSet)
router.register("stock-movements", StockMovementViewSet)

urlpatterns = [path("", include(router.urls))]
