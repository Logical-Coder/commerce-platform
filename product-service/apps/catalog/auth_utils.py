# Import settings to read JWT configuration
from django.conf import settings

# Import TokenError to catch invalid or expired token errors
from rest_framework_simplejwt.exceptions import TokenError

# Import AccessToken to decode and validate JWT access tokens
from rest_framework_simplejwt.tokens import AccessToken


# Extract JWT payload from Authorization header
def get_jwt_payload_from_request(request):
    # Read Authorization header from request
    auth_header = request.headers.get("Authorization")

    # Debug print to check incoming Authorization header
    print("Authorization Header:", auth_header)

    # If Authorization header is missing, return None
    if not auth_header:
        return None

    # If Authorization header is not Bearer token, return None
    if not auth_header.startswith("Bearer "):
        return None

    # Extract token value after "Bearer "
    token = auth_header.split(" ", 1)[1]

    try:
        # Print signing key length for debugging only
        print("Product JWT SIGNING_KEY length:", len(settings.SIMPLE_JWT["SIGNING_KEY"]))

        # Decode and validate the access token
        access_token = AccessToken(token)

        # Get payload correctly from AccessToken object
        payload = access_token.payload

        # Debug print decoded payload
        print("JWT Payload:", payload)

        # Return payload to permission class
        return payload

    except TokenError as exc:
        # Print exact token error
        print("JWT TokenError:", str(exc))

        # Return None if token invalid or expired
        return None

    except Exception as exc:
        # Print unexpected error
        print("JWT Unexpected Error:", repr(exc))

        # Return None for safety
        return None