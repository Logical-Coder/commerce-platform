from django.urls import path

# Import views
from .views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    ProductListCreateAPIView,
    ProductDetailAPIView,
    ProductStockUpdateAPIView,
    health,
)

urlpatterns = [
    # Category APIs
    path("categories/", CategoryListCreateAPIView.as_view()),
    path("categories/<int:pk>/", CategoryDetailAPIView.as_view()),
    # Product APIs
    path("products/", ProductListCreateAPIView.as_view()),
    path("products/<int:pk>/", ProductDetailAPIView.as_view()),
    path("products/<int:pk>/stock/", ProductStockUpdateAPIView.as_view()),
    path("health/", health, name="health"),
]
