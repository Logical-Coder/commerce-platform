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
    class Meta:
        # Map serializer to Product model
        model = Product

        # Fields to expose in API
        fields = "__all__"