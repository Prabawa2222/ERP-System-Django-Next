from django.db import models
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    UNIT_CHOICES = (
        ("piece", "Piece"),
        ("kg", "Kilogram"),
        ("g", "Gram"),
        ("l", "Liter"),
        ("ml", "Milliliter"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    price = models.DecimalField(max_length=10, decimal_places=2, max_digits=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    current_stock = models.IntegerField(default=0)
    min_stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"


class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ("purchase", "Purchase"),
        ("sale", "Sale"),
        ("adjustment", "Adjustment"),
        ("return", "Return"),
    )

    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stock_movements"
    )
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Update product stock
        if self.movement_type in ["purchase", "return"]:
            self.product.current_stock += self.quantity
        else:  # sale or adjustment
            self.product.current_stock -= self.quantity
        self.product.save()
        super().save(*args, **kwargs)
