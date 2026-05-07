from rest_framework.throttling import SimpleRateThrottle

from .auth_utils import get_jwt_payload_from_request


class JwtUserOrIPRateThrottle(SimpleRateThrottle):
    scope = "user"

    def get_cache_key(self, request, view):
        payload = get_jwt_payload_from_request(request)

        if payload:
            user_identifier = payload.get("user_id") or payload.get("email")
            if user_identifier:
                return self.cache_format % {
                    "scope": self.scope,
                    "ident": f"user:{user_identifier}",
                }

        return self.cache_format % {
            "scope": self.scope,
            "ident": f"ip:{self.get_ident(request)}",
        }
