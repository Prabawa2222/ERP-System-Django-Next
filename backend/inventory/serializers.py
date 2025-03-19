from rest_framework import serializers
from .models import Category, Product, StockMovement


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["id", "current_stock", "created_at", "updated_at"]


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = StockMovement
        fields = "__all__"
        read_only_fields = ["created_at"]
