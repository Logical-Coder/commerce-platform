# Import JsonResponse for simple health API
from django.http import JsonResponse

# Import DRF generic views for CRUD APIs
from rest_framework import generics

# Import models from catalog app
from .models import Category, Product

# Import ProductFilter for custom price and stock filtering
from .filters import ProductFilter

# Import serializers from catalog app
from .serializers import CategorySerializer, ProductSerializer

# Import custom permission for admin-only write operations
from .permissions import IsAdminOrReadOnly

# Health endpoint to verify product-service is running
def health(request):
    # Return basic service health response
    return JsonResponse(
        {
            # API status
            "status": "ok",

            # Service name
            "service": "product-service",
        }
    )


# API to list and create categories
class CategoryListCreateAPIView(generics.ListCreateAPIView):

    # Apply permission: public read, admin write
    permission_classes = [IsAdminOrReadOnly]

    # Fetch all category records from database
    queryset = Category.objects.all().order_by("id")

    # Use CategorySerializer for request/response conversion
    serializer_class = CategorySerializer

    # Allow filtering by these fields
    filterset_fields = ["is_active"]

    # Allow search by these fields
    search_fields = ["name", "slug", "description"]

    # Allow ordering by these fields
    ordering_fields = ["id", "name", "created_at"]

    # Default ordering
    ordering = ["id"]


# API to retrieve, update, and delete a single category
class CategoryDetailAPIView(generics.RetrieveUpdateDestroyAPIView):

    # Apply permission: public read, admin write
    permission_classes = [IsAdminOrReadOnly]

    # Fetch all category records
    queryset = Category.objects.all()

    # Use CategorySerializer
    serializer_class = CategorySerializer


# API to list and create products
class ProductListCreateAPIView(generics.ListCreateAPIView):

    # Apply permission: public read, admin write
    permission_classes = [IsAdminOrReadOnly]

    # Fetch products with related category using select_related to avoid N+1 queries
    queryset = Product.objects.select_related("category").all().order_by("id")

    # Use ProductSerializer for request/response conversion
    serializer_class = ProductSerializer

    # Allow exact filtering by these fields
    filterset_class = ProductFilter

    # Allow search by these fields
    search_fields = [
        "name",
        "slug",
        "description",
        "category__name",
    ]

    # Allow ordering by these fields
    ordering_fields = [
        "id",
        "name",
        "price",
        "stock_quantity",
        "created_at",
    ]

    # Default ordering
    ordering = ["id"]


# API to retrieve, update, and delete a single product
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):

    # Apply permission: public read, admin write
    permission_classes = [IsAdminOrReadOnly]
    
    # Fetch products with related category
    queryset = Product.objects.select_related("category").all()

    # Use ProductSerializer
    serializer_class = ProductSerializer