import base64
import json

from rest_framework.throttling import SimpleRateThrottle


def get_jwt_payload(request):
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return {}

    token = auth_header.split(" ", 1)[1]
    parts = token.split(".")
    if len(parts) < 2:
        return {}

    try:
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload.encode("ascii")))
    except (ValueError, TypeError, json.JSONDecodeError):
        return {}


class JwtUserOrIPRateThrottle(SimpleRateThrottle):
    scope = "user"

    def get_cache_key(self, request, view):
        payload = get_jwt_payload(request)
        user_identifier = payload.get("user_id") or payload.get("email")

        if user_identifier:
            ident = f"user:{user_identifier}"
        else:
            ident = f"ip:{self.get_ident(request)}"

        return self.cache_format % {"scope": self.scope, "ident": ident}
