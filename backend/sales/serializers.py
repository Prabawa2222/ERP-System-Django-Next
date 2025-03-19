from rest_framework import serializers
from .models import Customer, Sale, SaleItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = "__all__"
        read_only_fields = ["created_at"]


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_sku = serializers.ReadOnlyField(source="product.sku")

    class Meta:
        model = SaleItem
        fields = [
            "id",
            "product",
            "product_name",
            "product_sku",
            "quantity",
            "unit_price",
            "subtotal",
        ]
        read_only_fields = ["subtotal"]


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, read_only=True)
    customer_name = serializers.ReadOnlyField(source="customer.name")
    created_by_name = serializers.ReadOnlyField(source="created_by.username")

    class Meta:
        model = Sale
        fields = [
            "id",
            "customer",
            "customer_name",
            "invoice_number",
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


class SaleCreateSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True)

    class Meta:
        model = Sale
        fields = ["customer", "invoice_number", "status", "notes", "items"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        validated_data["created_by"] = self.context["request"].user
        sale = Sale.objects.create(**validated_data)

        for item_data in items_data:
            product = item_data["product"]
            quantity = item_data["quantity"]
            unit_price = item_data["unit_price"]

            # Create the sale item
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=quantity * unit_price,
            )

            # Update product stock via StockMovement model
            from inventory.models import StockMovement

            StockMovement.objects.create(
                product=product,
                quantity=quantity,
                movement_type="sale",
                reference=f"Sale {sale.invoice_number}",
                notes=f"Item sold in sale {sale.invoice_number}",
            )

        # Calculate total
        sale.total_amount = sum(item.subtotal for item in sale.items.all())
        sale.save()

        return sale
