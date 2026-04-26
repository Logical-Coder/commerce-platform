# Import django-filter package for creating custom filters
import django_filters

# Import Product model
from .models import Product


# ProductFilter handles custom filtering for product APIs
class ProductFilter(django_filters.FilterSet):
    # Filter products where price is greater than or equal to given value
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")

    # Filter products where price is less than or equal to given value
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    # Filter products where stock quantity is greater than or equal to given value
    min_stock = django_filters.NumberFilter(
        field_name="stock_quantity",
        lookup_expr="gte",
    )

    # Filter products where stock quantity is less than or equal to given value
    max_stock = django_filters.NumberFilter(
        field_name="stock_quantity",
        lookup_expr="lte",
    )

    # Meta class defines model and normal exact-match filter fields
    class Meta:
        # Use Product model for this filter
        model = Product

        # Allow normal filters plus custom filters above
        fields = [
            "category",
            "is_active",
            "min_price",
            "max_price",
            "min_stock",
            "max_stock",
        ]