# Import Python logging module
import logging

# Import Django JSON response helper
from django.http import JsonResponse

# Import Django DB connection helper
from django.db import connection

# Import redis package
import redis

# Import DRF APIView base class
from rest_framework.views import APIView

# Import DRF Response helper
from rest_framework.response import Response

# Import DRF status codes
from rest_framework import status

# Import serializers
from apps.accounts.serializers import RegisterSerializer, LoginSerializer

# Import service layer
from apps.accounts.services import AccountService

# Import permission class to protect API
from rest_framework.permissions import IsAuthenticated

# Import account response serializer
from apps.accounts.serializers import AccountProfileSerializer

# Import custom role permission
from apps.accounts.permissions import IsAdminRole

# Create logger for this file
logger = logging.getLogger(__name__)


# Basic health endpoint
def health(request):
    # Log request arrival
    logger.info("[VIEW] /health called")

    # Return JSON response
    return JsonResponse({"status": "ok", "service": "identity-service-django"})


# Database health endpoint
def health_db(request):
    # Log request arrival
    logger.info("[VIEW] /health/db called")

    try:
        # Open cursor on configured database
        with connection.cursor() as cursor:
            # Execute test query
            cursor.execute("SELECT 1")

            # Fetch first row
            row = cursor.fetchone()

        # Log successful DB test
        logger.info("[DB] SELECT 1 result: %s", row)

        # Return success response
        return JsonResponse({"status": "ok", "database": "mysql"})
    except Exception as exc:
        # Log DB error
        logger.error("[DB] connection failed: %s", str(exc))

        # Return error response
        return JsonResponse({"status": "error", "detail": str(exc)}, status=500)


# Redis health endpoint
def health_redis(request):
    # Log request arrival
    logger.info("[VIEW] /health/redis called")

    try:
        # Create Redis client
        r = redis.Redis(host="127.0.0.1", port=6379, db=0, decode_responses=True)

        # Ping Redis
        pong = r.ping()

        # Log successful ping
        logger.info("[REDIS] ping: %s", pong)

        # Return success response
        return JsonResponse({"status": "ok", "redis": "connected"})
    except Exception as exc:
        # Log Redis error
        logger.error("[REDIS] connection failed: %s", str(exc))

        # Return error response
        return JsonResponse({"status": "error", "detail": str(exc)}, status=500)


# Register API view
class RegisterAPIView(APIView):
    # Handle POST request for register
    def post(self, request):
        # Log that request entered register view
        logger.info("[VIEW] RegisterAPIView POST called")

        # Log raw request data
        logger.info("[VIEW] Register request data: %s", request.data)

        # Create serializer with incoming request data
        serializer = RegisterSerializer(data=request.data)

        # Validate request
        if not serializer.is_valid():
            # Log serializer errors
            logger.warning(
                "[VIEW] Register serializer validation failed: %s", serializer.errors
            )

            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create service object
            service = AccountService()

            # Call register business logic
            account = service.register_account(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )

            # Log successful registration
            logger.info("[VIEW] Account registered successfully with id=%s", account.id)

            # Return success response
            return Response(
                {
                    "message": "Account registered successfully",
                    "id": account.id,
                    "email": account.email,
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as exc:
            # Log known business error
            logger.warning("[VIEW] Register business validation failed: %s", str(exc))

            # Return controlled business error
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as exc:
            # Log unexpected error with traceback
            logger.exception("[VIEW] Unexpected error during registration")

            # Return generic server error
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Login API view
class LoginAPIView(APIView):
    # Handle POST request for login
    def post(self, request):
        # Log that request entered login view
        logger.info("[VIEW] LoginAPIView POST called")

        # Log incoming request data except sensitive values in real projects
        logger.info(
            "[VIEW] Login request data: %s", {"email": request.data.get("email")}
        )

        # Create serializer with request data
        serializer = LoginSerializer(data=request.data)

        # Validate request
        if not serializer.is_valid():
            # Log serializer validation error
            logger.warning(
                "[VIEW] Login serializer validation failed: %s", serializer.errors
            )

            # Return validation error response
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create service instance
            service = AccountService()

            # Call login business logic
            result = service.login_account(
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
            )

            # Log successful login
            logger.info(
                "[VIEW] Login successful for account id=%s", result["account"].id
            )

            # Return JWT tokens and minimal user data
            return Response(
                {
                    "message": "Login successful",
                    "access": result["access"],
                    "refresh": result["refresh"],
                    "account": {
                        "id": result["account"].id,
                        "email": result["account"].email,
                        "role": result["account"].role,
                        "account_status": result["account"].account_status,
                    },
                },
                status=status.HTTP_200_OK,
            )

        except ValueError as exc:
            # Log known login failure
            logger.warning("[VIEW] Login failed: %s", str(exc))

            # Return unauthorized response
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        except Exception as exc:
            # Log unexpected exception with traceback
            logger.exception("[VIEW] Unexpected error during login")

            # Return generic server error
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Protected API to return current logged-in account details
class MeAPIView(APIView):
    # Only authenticated users can access this API
    permission_classes = [IsAuthenticated]

    # Handle GET request
    def get(self, request):
        # Log that /me API was called
        logger.info("[VIEW] MeAPIView GET called")

        # Get current authenticated user from request
        account = request.user

        # Log authenticated account id
        logger.info("[VIEW] Current account id=%s", account.id)

        # Convert account object into response data
        serializer = AccountProfileSerializer(account)

        # Return serialized account data
        return Response(serializer.data, status=status.HTTP_200_OK)


# API only ADMIN can access
class AdminOnlyAPIView(APIView):
    # User must be logged in and must be ADMIN
    permission_classes = [IsAuthenticated, IsAdminRole]

    # Handle GET request
    def get(self, request):
        # Log admin API call
        logger.info("[VIEW] AdminOnlyAPIView GET called by user id=%s", request.user.id)

        # Return success response
        return Response(
            {
                "message": "Welcome ADMIN",
                "email": request.user.email,
                "role": request.user.role,
            },
            status=status.HTTP_200_OK,
        )
