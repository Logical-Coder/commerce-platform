# Import DRF serializers
from rest_framework import serializers

# Import models
from .models import Category, Product


# Serializer for Category model
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        # Map serializer to Category model
        model = Category

        # Fields to expose in API
        fields = ["id", "name", "slug", "description", "is_active"]


# Serializer for Product model
class ProductSerializer(serializers.ModelSerializer):
    # Expose computed stock availability
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        # Map serializer to Product model
        model = Product

        # Fields to expose in API
        fields = "__all__"


# Serializer for admin stock updates
class ProductStockUpdateSerializer(serializers.ModelSerializer):
    # Expose computed stock availability in response
    stock_status = serializers.CharField(read_only=True)

    class Meta:
        # Map serializer to Product model
        model = Product

        # Allow admins to update stock only
        fields = ["id", "name", "stock_quantity", "stock_status"]

        # Product id and name are response-only
        read_only_fields = ["id", "name", "stock_status"]

    # Validate required request shape
    def validate(self, attrs):
        if "stock_quantity" not in self.initial_data:
            raise serializers.ValidationError(
                {"stock_quantity": "This field is required."}
            )

        return attrs

    # Validate stock quantity business rule
    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Stock quantity cannot be negative.")

        return value
