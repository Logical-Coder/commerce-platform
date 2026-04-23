# Import Python logging module
import logging

# Import repository layer
from apps.accounts.repositories import AccountRepository

# Import JWT refresh token helper from simplejwt
from rest_framework_simplejwt.tokens import RefreshToken


# Create logger for this module
logger = logging.getLogger(__name__)


# Service class for account-related business logic
class AccountService:
    # Constructor to prepare repository instance
    def __init__(self):
        # Store repository object on service instance
        self.repository = AccountRepository()

    # Business logic for account registration
    def register_account(self, email, password):
        # Log service entry
        logger.info("[SERVICE] Register account started for email=%s", email)

        # Check whether same email already exists
        existing_account = self.repository.get_by_email(email)

        # If found, stop registration
        if existing_account:
            logger.warning("[SERVICE] Account already exists for email=%s", email)
            raise ValueError("Email already registered")

        # Create account in database
        account = self.repository.create_account(
            email=email,
            password=password,
            role="CUSTOMER",
            account_status="ACTIVE",
            is_email_verified=False,
        )

        # Log completion
        logger.info("[SERVICE] Register account completed for id=%s", account.id)

        # Return created account
        return account

    # Business logic for login
    def login_account(self, email, password):
        # Log login start
        logger.info("[SERVICE] Login account started for email=%s", email)

        # Fetch account by email from database
        account = self.repository.get_by_email(email)

        # If account not found, reject login
        if not account:
            logger.warning("[SERVICE] Account not found for email=%s", email)
            raise ValueError("Invalid email or password")

        # Log that account was found
        logger.info("[SERVICE] Account found with id=%s", account.id)

        # Check password using Django's built-in password checker
        if not account.check_password(password):
            logger.warning("[SERVICE] Password mismatch for email=%s", email)
            raise ValueError("Invalid email or password")

        # Check account status before allowing login
        if account.account_status != "ACTIVE":
            logger.warning("[SERVICE] Account is not active for email=%s", email)
            raise ValueError("Account is not active")

        # Log successful password verification
        logger.info("[SERVICE] Password verified successfully for email=%s", email)

        # Create JWT refresh token object for this account
        refresh = RefreshToken.for_user(account)

        # Log token generation
        logger.info("[SERVICE] JWT tokens generated for account id=%s", account.id)

        # Return both refresh and access token as strings
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "account": account,
        }