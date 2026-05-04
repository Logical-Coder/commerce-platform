# Import TokenError to catch invalid or expired token errors
from rest_framework_simplejwt.exceptions import TokenError

# Import AccessToken to decode and validate JWT access tokens
from rest_framework_simplejwt.tokens import AccessToken


# Extract JWT payload from Authorization header
def get_jwt_payload_from_request(request):
    # Read Authorization header from request
    auth_header = request.headers.get("Authorization")

    # If Authorization header is missing, return None
    if not auth_header:
        return None

    # If Authorization header is not Bearer token, return None
    if not auth_header.startswith("Bearer "):
        return None

    # Extract token value after "Bearer "
    token = auth_header.split(" ", 1)[1]

    try:

        # Decode and validate the access token
        access_token = AccessToken(token)

        # Get payload correctly from AccessToken object
        payload = access_token.payload

        # Return payload to permission class
        return payload

    except TokenError:
        # Return None if token invalid or expired
        return None

    except Exception:
        # Return None for safety
        return None
