from django.urls import path

# Import views
from .views import (
    CategoryListCreateAPIView,
    CategoryDetailAPIView,
    ProductListCreateAPIView,
    ProductDetailAPIView,
)

urlpatterns = [
    # Category APIs
    path("categories", CategoryListCreateAPIView.as_view()),
    path("categories/<int:pk>", CategoryDetailAPIView.as_view()),

    # Product APIs
    path("products", ProductListCreateAPIView.as_view()),
    path("products/<int:pk>", ProductDetailAPIView.as_view()),
]