from unittest.mock import Mock, patch

import requests
from django.conf import settings
from django.core.cache import cache
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient


class GatewayProxyTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()

    def test_health_api_success(self):
        response = self.client.get("/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["service"], "api-gateway")

    @patch("gateway.views.requests.request")
    def test_auth_requests_proxy_to_identity_service(self, mock_request):
        mock_request.return_value = Mock(
            content=b'{"ok":true}',
            status_code=status.HTTP_200_OK,
            headers={"Content-Type": "application/json"},
        )

        response = self.client.post(
            "/api/auth/login",
            {"email": "test@example.com", "password": "secret123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            mock_request.call_args.kwargs["url"],
            f"{settings.IDENTITY_SERVICE_URL}/api/auth/login",
        )

    @patch("gateway.views.requests.request")
    def test_product_requests_proxy_to_product_service(self, mock_request):
        mock_request.return_value = Mock(
            content=b'{"count":0,"results":[]}',
            status_code=status.HTTP_200_OK,
            headers={"Content-Type": "application/json"},
        )

        response = self.client.get("/api/products/?search=seed")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            mock_request.call_args.kwargs["url"],
            f"{settings.PRODUCT_SERVICE_URL}/api/products/?search=seed",
        )

    @patch("gateway.views.requests.request")
    def test_gateway_forwards_auth_and_host_headers(self, mock_request):
        mock_request.return_value = Mock(
            content=b"{}",
            status_code=status.HTTP_200_OK,
            headers={"Content-Type": "application/json"},
        )

        response = self.client.get(
            "/api/products/",
            HTTP_AUTHORIZATION="Bearer test-token",
            HTTP_HOST="localhost:8080",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        headers = mock_request.call_args.kwargs["headers"]
        self.assertEqual(headers["Authorization"], "Bearer test-token")
        self.assertEqual(headers["Host"], "localhost:8080")
        self.assertEqual(headers["X-Forwarded-Host"], "localhost:8080")

    def test_unknown_route_returns_404(self):
        response = self.client.get("/api/orders/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch("gateway.views.requests.request")
    def test_upstream_unavailable_returns_502(self, mock_request):
        mock_request.side_effect = requests.ConnectionError("network down")

        response = self.client.get("/api/products/")

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertEqual(response.json()["detail"], "Upstream service is unavailable.")

    @patch("gateway.views.requests.request")
    def test_gateway_rate_limits_requests(self, mock_request):
        mock_request.return_value = Mock(
            content=b"{}",
            status_code=status.HTTP_200_OK,
            headers={"Content-Type": "application/json"},
        )

        for _ in range(50):
            self.assertEqual(self.client.get("/api/products/").status_code, 200)

        self.assertEqual(
            self.client.get("/api/products/").status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )
