# Import Django path function
from django.urls import path

# Import views from current app
from .views import health, health_db, health_redis, RegisterAPIView, LoginAPIView


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
]