from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Customer, Sale, SaleItem
from .serializers import (
    CustomerSerializer,
    SaleSerializer,
    SaleItemSerializer,
    SaleCreateSerializer,
)
from core.permissions import IsAdminOrManager


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["name", "email"]
    search_fields = ["name", "email", "phone"]


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all().order_by("-created_at")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["invoice_number", "customer__name", "notes"]

    def get_serializer_class(self):
        if self.action == "create":
            return SaleCreateSerializer
        return SaleSerializer

    def get_permissions(self):
        if self.action in ["destroy", "update", "partial_update"]:
            return [IsAdminOrManager]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        sale = self.get_object()
        new_status = request.data.get("status")

        if new_status not in dict(Sale.STATUS_CHOICES).keys():
            return Response(
                {
                    "status": f"Invalid status. Choose from {dict(Sale.STATUS_CHOICES).keys()}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        sale.status = new_status
        sale.save()

        return Response({"status": f"Sale status updated to {new_status}"})


class SaleItemViewSet(viewsets.ModelViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["sale", "product"]

    def get_permissions(self):
        if self.action in ["create", "destroy", "update", "partial_update"]:
            return [IsAdminOrManager]
        return super().get_permissions()
