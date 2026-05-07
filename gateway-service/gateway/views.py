from urllib.parse import urljoin

import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from rest_framework.views import APIView

HOP_BY_HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}


def health(request):
    return JsonResponse({"status": "ok", "service": "api-gateway"})


class GatewayProxyView(APIView):
    http_method_names = ["get", "post", "put", "patch", "delete", "head", "options"]

    def dispatch(self, request, *args, **kwargs):
        path = kwargs.get("path", "")
        if not self.get_target_base_url(path):
            return JsonResponse(
                {
                    "detail": "No upstream route configured for this path.",
                    "path": f"/{path}",
                },
                status=404,
            )

        return super().dispatch(request, *args, **kwargs)

    def get_target_base_url(self, path):
        if path.startswith("api/auth/"):
            return settings.IDENTITY_SERVICE_URL

        if path.startswith("api/products/") or path == "api/products":
            return settings.PRODUCT_SERVICE_URL

        if path.startswith("api/categories/") or path == "api/categories":
            return settings.PRODUCT_SERVICE_URL

        if path in {"identity/health", "identity/health/db", "identity/health/redis"}:
            return settings.IDENTITY_SERVICE_URL

        if path == "product/health":
            return settings.PRODUCT_SERVICE_URL

        return None

    def get_upstream_path(self, path):
        if path.startswith("identity/"):
            return path.removeprefix("identity/")

        if path.startswith("product/"):
            return f"api/{path.removeprefix('product/')}"

        return path

    def proxy(self, request, path):
        base_url = self.get_target_base_url(path)
        upstream_path = self.get_upstream_path(path)
        upstream_url = urljoin(base_url.rstrip("/") + "/", upstream_path)

        if request.META.get("QUERY_STRING"):
            upstream_url = f"{upstream_url}?{request.META['QUERY_STRING']}"

        headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in HOP_BY_HOP_HEADERS
        }
        headers["X-Forwarded-Host"] = request.get_host()
        headers["X-Forwarded-Proto"] = request.scheme
        headers["Host"] = request.get_host()

        try:
            upstream_response = requests.request(
                method=request.method,
                url=upstream_url,
                headers=headers,
                data=request.body,
                timeout=settings.GATEWAY_REQUEST_TIMEOUT,
                allow_redirects=False,
            )
        except requests.RequestException as exc:
            return JsonResponse(
                {
                    "detail": "Upstream service is unavailable.",
                    "error": str(exc),
                },
                status=502,
            )

        response = HttpResponse(
            upstream_response.content,
            status=upstream_response.status_code,
        )

        for key, value in upstream_response.headers.items():
            if key.lower() not in HOP_BY_HOP_HEADERS:
                response[key] = value

        return response

    def get(self, request, path=""):
        return self.proxy(request, path)

    def post(self, request, path=""):
        return self.proxy(request, path)

    def put(self, request, path=""):
        return self.proxy(request, path)

    def patch(self, request, path=""):
        return self.proxy(request, path)

    def delete(self, request, path=""):
        return self.proxy(request, path)

    def head(self, request, path=""):
        return self.proxy(request, path)

    def options(self, request, path=""):
        return self.proxy(request, path)
