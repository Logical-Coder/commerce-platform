# Import Django model classes
from django.db import models


class TimestampedModel(models.Model):
    # Abstract base model to add created_at and updated_at fields
    created_at = models.DateTimeField(auto_now_add=True)
    # updated_at is automatically updated to current time on each save
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Category table stores product categories like Seeds, Nuts, Grains
class Category(TimestampedModel):
    # Category name, example: "Seeds"
    name = models.CharField(max_length=100, unique=True)

    # Slug is URL-friendly name, example: "sunflower-seeds"
    slug = models.SlugField(max_length=120, unique=True)

    # Optional category description
    description = models.TextField(blank=True, null=True)

    # Controls whether category is active or hidden
    is_active = models.BooleanField(default=True)

    # Database table name
    class Meta:
        db_table = "categories"

    # Human-readable object display
    def __str__(self):
        return self.name


# Product table stores actual product details
class Product(TimestampedModel):
    # Product category relationship
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
    )

    # Product name, example: "Sunflower Seeds"
    name = models.CharField(max_length=150)

    # URL-friendly product slug
    slug = models.SlugField(max_length=180, unique=True)

    # Product description
    description = models.TextField(blank=True, null=True)

    # Product price
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Available stock quantity
    stock_quantity = models.PositiveIntegerField(default=0)

    # Product active/inactive flag
    is_active = models.BooleanField(default=True)

    # Database table name
    class Meta:
        db_table = "products"

    # Human-readable object display
    def __str__(self):
        return self.name
