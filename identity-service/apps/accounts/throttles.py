from rest_framework.throttling import SimpleRateThrottle


class UserOrIPRateThrottle(SimpleRateThrottle):
    scope = "user"

    def get_cache_key(self, request, view):
        user = getattr(request, "user", None)

        if user and user.is_authenticated:
            return self.cache_format % {
                "scope": self.scope,
                "ident": f"user:{user.pk}",
            }

        return self.cache_format % {
            "scope": self.scope,
            "ident": f"ip:{self.get_ident(request)}",
        }
