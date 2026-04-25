# Import logging
import logging

# Import DRF permission base class
from rest_framework.permissions import BasePermission

# Create logger
logger = logging.getLogger(__name__)


# Permission class to allow only ADMIN users
class IsAdminRole(BasePermission):
    # Custom error message
    message = "Only ADMIN users can access this API"

    # Permission check method
    def has_permission(self, request, view):
        # Get current user
        user = request.user

        # Log permission check
        logger.info("[PERMISSION] Checking ADMIN role for user=%s", user)

        # Return True only if user is authenticated and role is ADMIN
        return bool(user and user.is_authenticated and user.role == "ADMIN")


# Permission class to allow only CUSTOMER users
class IsCustomerRole(BasePermission):
    # Custom error message
    message = "Only CUSTOMER users can access this API"

    # Permission check method
    def has_permission(self, request, view):
        # Get current user
        user = request.user

        # Log permission check
        logger.info("[PERMISSION] Checking CUSTOMER role for user=%s", user)

        # Return True only if user is authenticated and role is CUSTOMER
        return bool(user and user.is_authenticated and user.role == "CUSTOMER")
