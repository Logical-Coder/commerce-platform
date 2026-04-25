# Import Django path function
from django.urls import path

# Import views from current app

from .views import (
    health,
    health_db,
    health_redis,
    RegisterAPIView,
    LoginAPIView,
    MeAPIView,
    AdminOnlyAPIView,
)

# URL patterns for this app
urlpatterns = [
    # Health endpoint
    path("health", health, name="health"),
    # Database health endpoint
    path("health/db", health_db, name="health-db"),
    # Redis health endpoint
    path("health/redis", health_redis, name="health-redis"),
    # Register endpoint
    path("api/auth/register", RegisterAPIView.as_view(), name="register"),
    # Login endpoint
    path("api/auth/login", LoginAPIView.as_view(), name="login"),
    # Protected current user endpoint
    path("api/auth/me", MeAPIView.as_view(), name="me"),
    # Admin-only endpoint
    path("api/auth/admin-only", AdminOnlyAPIView.as_view(), name="admin-only"),
]
