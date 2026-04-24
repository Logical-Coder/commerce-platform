# Import Python logging module for structured logging
import logging

# Import DRF serializer tools
from rest_framework import serializers

# Create a logger object for this file
logger = logging.getLogger(__name__)


# Serializer for register request input
class RegisterSerializer(serializers.Serializer):
    # Email field with built-in email validation
    email = serializers.EmailField()

    # Password field, write_only means it won't be sent back in API response
    password = serializers.CharField(write_only=True, min_length=6)

    # Custom validation hook
    def validate(self, attrs):
        # Log that register validation started
        logger.info("[SERIALIZER] Register validation started")

        # Log email only, never log raw password in real applications
        logger.info("[SERIALIZER] Register email received: %s", attrs.get("email"))

        # Return validated attributes
        return attrs


# Serializer for login request input
class LoginSerializer(serializers.Serializer):
    # Email field with built-in validation
    email = serializers.EmailField()

    # Password field, write_only avoids returning it in response
    password = serializers.CharField(write_only=True)

    # Custom validation hook
    def validate(self, attrs):
        # Log that login validation started
        logger.info("[SERIALIZER] Login validation started")

        # Log incoming email
        logger.info("[SERIALIZER] Login email received: %s", attrs.get("email"))

        # Return validated data
        return attrs
