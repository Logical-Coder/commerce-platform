# Import Python logging module
import logging

# Import Account model
from apps.accounts.models import Account

# Create logger for this module
logger = logging.getLogger(__name__)


# Repository class to isolate DB queries from business logic
class AccountRepository:
    # Fetch account by email
    def get_by_email(self, email):
        # Log that repository is querying database
        logger.info("[REPOSITORY] Fetching account by email=%s", email)

        # Query database and return first match or None
        return Account.objects.filter(email=email).first()

    # Create a new account using custom manager
    def create_account(self, email, password, **extra_fields):
        # Log that account creation is starting
        logger.info("[REPOSITORY] Creating account for email=%s", email)

        # Use custom manager create_user so password is hashed correctly
        account = Account.objects.create_user(
            email=email, password=password, **extra_fields
        )

        # Log successful DB creation
        logger.info("[REPOSITORY] Account created with id=%s", account.id)

        # Return created object
        return account
