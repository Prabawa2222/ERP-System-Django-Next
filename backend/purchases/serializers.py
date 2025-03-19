from rest_framework import serializers
from .models import Supplier, Purchase, PurchaseItem


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"
        read_only_fields = ["created_at"]


class PurchaseItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_sku = serializers.ReadOnlyField(source="product.sku")

    class Meta:
        model = PurchaseItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "received_quantity",
            "unit_price",
            "subtotal",
        ]
        read_only_fields = ["subtotal"]


class PurchaseSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True, read_only=True)
    supplier_name = serializers.ReadOnlyField(source="supplier.name")
    created_by_name = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Purchase
        fields = [
            "id",
            "supplier",
            "supplier_name",
            "po_number",
            "status",
            "created_by",
            "created_by_name",
            "notes",
            "total_amount",
            "created_at",
            "updated_at",
            "items",
        ]
        read_only_fields = ["id", "total_amount", "created_at", "updated_at"]


class PurchaseCreateSerializer(serializers.ModelSerializer):
    items = PurchaseItemSerializer(many=True)

    class Meta:
        model = Purchase
        fields = ["supplier", "po_number", "status", "notes", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        validated_data["created_by"] = self.context["request"].user
        purchase = Purchase.objects.create(**validated_data)

        for item_data in items_data:
            PurchaseItem.objects.create(purchase=purchase, **item_data)

        # Calculate total
        purchase.total_amount = sum(item.subtotal for item in purchase.items.all())
        purchase.save()

        return purchase


class PurchaseItemReceiveSerializer(serializers.Serializer):
    received_quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        purchase_item = self.context["purchase_item"]
        new_received_qty = data["received_quantity"]

        # Check if the new received quantity is valid
        if new_received_qty > (
            purchase_item.quantity - purchase_item.received_quantity
        ):
            raise serializers.ValidationError(
                "Received quantity cannot exceed remaining quantity"
            )

        return data
