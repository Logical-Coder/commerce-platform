# Import DRF base permission and safe methods
from rest_framework.permissions import BasePermission, SAFE_METHODS

# Import helper to decode JWT payload
from .auth_utils import get_jwt_payload_from_request


# Permission: anyone can read, only ADMIN can write
class IsAdminOrReadOnly(BasePermission):
    # Message returned when write access is denied
    message = "Only ADMIN users can modify this resource"

    # DRF calls this method before executing the view
    def has_permission(self, request, view):
        # Allow public GET, HEAD, OPTIONS requests
        if request.method in SAFE_METHODS:
            return True
    

        # Extract JWT payload from Authorization header
        payload = get_jwt_payload_from_request(request)

        # If token is missing or invalid, deny access
        print("JWT Payload:", payload)  # Debug print to check payload content
        
        if not payload:
            return False

        # Read role from JWT payload
        role = payload.get("role")

        # Allow write only if role is ADMIN
        return role == "ADMIN"