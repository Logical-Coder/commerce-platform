from django.urls import path, re_path

from gateway.views import GatewayProxyView, health

urlpatterns = [
    path("health/", health, name="health"),
    re_path(r"^(?P<path>.*)$", GatewayProxyView.as_view(), name="gateway-proxy"),
]
