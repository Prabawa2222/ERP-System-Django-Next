from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Supplier, Purchase, PurchaseItem
from .serializers import (
    SupplierSerializer,
    PurchaseSerializer,
    PurchaseItemSerializer,
    PurchaseCreateSerializer,
    PurchaseItemReceiveSerializer,
)
from core.permissions import IsAdminOrManager
from inventory.models import StockMovement


class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["name"]
    search_fields = ["name", "contact_person", "email", "phone"]


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all().order_by("-created_at")
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["supplier", "status", "created_at"]
    search_fields = ["po_number", "supplier__name", "notes"]

    def get_serializer_class(self):
        if self.action == "create":
            return PurchaseCreateSerializer
        return PurchaseSerializer

    def get_permissions(self):
        if self.action in ["destroy"]:
            return [IsAdminOrManager()]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def change_status(self, request, pk=None):
        purchase = self.get_object()
        new_status = request.data.get("status")

        if new_status not in dict(Purchase.STATUS_CHOICES).keys():
            return Response(
                {
                    "status": f"Invalid status. Choose from {dict(Purchase.STATUS_CHOICES).keys()}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        purchase.status = new_status
        purchase.save()

        return Response({"status": f"Purchase status updated to {new_status}"})


class PurchaseItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseItem.objects.all()
    serializer_class = PurchaseItemSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["purchase", "product"]

    def get_permissions(self):
        if self.action in ["destroy"]:
            return [IsAdminOrManager()]
        return super().get_permissions()

    @action(detail=True, methods=["post"])
    def receive(self, request, pk=None):
        purchase_item = self.get_object()

        # Check if the purchase is not cancelled
        if purchase_item.purchase.status == "cancelled":
            return Response(
                {"error": "Cannot receive items for a cancelled purchase order"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PurchaseItemReceiveSerializer(
            data=request.data, context={"purchase_item": purchase_item}
        )

        if serializer.is_valid():
            received_qty = serializer.validated_data["received_quantity"]

            # Update received quantity
            purchase_item.received_quantity += received_qty
            purchase_item.save()

            # Create stock movement
            StockMovement.objects.create(
                product=purchase_item.product,
                quantity=received_qty,
                movement_type="purchase",
                reference=f"PO {purchase_item.purchase.po_number}",
                notes=f"Item received from purchase {purchase_item.purchase.po_number}",
            )

            # Check if we need to update the purchase status
            purchase = purchase_item.purchase

            # Check if all items are fully received
            all_items_received = all(
                item.received_quantity >= item.quantity for item in purchase.items.all()
            )

            # Check if some items are partially received
            some_items_received = any(
                item.received_quantity > 0 for item in purchase.items.all()
            )

            if all_items_received:
                purchase.status = "received"
            elif some_items_received:
                purchase.status = "partial"
            purchase.save()

            return Response(
                {
                    "status": "success",
                    "message": f"Received {received_qty} units",
                    "purchase_status": purchase.status,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
