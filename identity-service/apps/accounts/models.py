# Import Django's built-in logging support through Python logging
import logging

# Import Django model base classes and field types
from django.db import models

# Import classes needed to build a custom authentication model
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)

# Create a logger object for this file/module
# __name__ helps identify which file produced the log
logger = logging.getLogger(__name__)


# Custom manager for our Account model
# A manager controls how objects are created/fetched at a high level
class AccountManager(BaseUserManager):
    # Method to create a normal user
    def create_user(self, email, password=None, **extra_fields):
        # Log that user creation has started
        logger.info("[MANAGER] create_user called")

        # Validate that email is provided
        if not email:
            logger.error("[MANAGER] Email is required but not provided")
            raise ValueError("Email is required")

        # Normalize email to a standard format
        # Example: Test@Mail.com -> Test@mail.com depending on backend behavior
        email = self.normalize_email(email)

        # Log the normalized email
        logger.info("[MANAGER] Normalized email: %s", email)

        # Create a model instance but do not save it yet
        # self.model refers to the Account model
        user = self.model(email=email, **extra_fields)

        # Log that the Account object has been created in memory
        logger.info("[MANAGER] Account object created in memory")

        # Hash the password properly using Django's built-in password hashing
        # Never store raw passwords directly
        user.set_password(password)

        # Log that password hashing is complete
        logger.info("[MANAGER] Password hashed successfully")

        # Save the user to the database
        user.save(using=self._db)

        # Log successful save with generated primary key
        logger.info("[MANAGER] User saved to DB with id=%s", user.id)

        # Return the created user object
        return user

    # Method to create a superuser/admin account
    def create_superuser(self, email, password=None, **extra_fields):
        # Log that superuser creation has started
        logger.info("[MANAGER] create_superuser called")

        # Set default values required for admin users
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("account_status", "ACTIVE")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_email_verified", True)

        # Ensure is_staff is True for superuser
        if extra_fields.get("is_staff") is not True:
            logger.error("[MANAGER] Superuser must have is_staff=True")
            raise ValueError("Superuser must have is_staff=True")

        # Ensure is_superuser is True for superuser
        if extra_fields.get("is_superuser") is not True:
            logger.error("[MANAGER] Superuser must have is_superuser=True")
            raise ValueError("Superuser must have is_superuser=True")

        # Reuse create_user logic to keep password hashing and save flow centralized
        return self.create_user(email, password, **extra_fields)


# Custom Account model
# AbstractBaseUser gives password and authentication core behavior
# PermissionsMixin gives group and permission support
class Account(AbstractBaseUser, PermissionsMixin):
    # Choices for role field
    ROLE_CHOICES = (
        ("ADMIN", "ADMIN"),
        ("CUSTOMER", "CUSTOMER"),
        ("MANAGER", "MANAGER"),
    )

    # Choices for account status field
    STATUS_CHOICES = (
        ("ACTIVE", "ACTIVE"),
        ("INACTIVE", "INACTIVE"),
        ("SUSPENDED", "SUSPENDED"),
    )

    # Email will be the main login field and must be unique
    email = models.EmailField(unique=True)

    # Role tells what kind of user this is
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default="CUSTOMER")

    # Account status lets us disable or suspend users without deleting them
    account_status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="ACTIVE"
    )

    # This tells whether email verification has happened
    is_email_verified = models.BooleanField(default=False)

    # Required by Django admin and permission system
    is_staff = models.BooleanField(default=False)

    # Required by Django auth system
    # Usually keep True unless soft-disabling user login
    is_active = models.BooleanField(default=True)

    # Auto-set when record is first created
    created_at = models.DateTimeField(auto_now_add=True)

    # Auto-updated every time the record is modified
    updated_at = models.DateTimeField(auto_now=True)

    # Attach custom manager to this model
    objects = AccountManager()

    # Tell Django to use email instead of username for login
    USERNAME_FIELD = "email"

    # No additional required fields when creating superuser interactively
    REQUIRED_FIELDS = []

    # Meta options for table configuration
    class Meta:
        # Force Django to use this exact MySQL table name
        db_table = "accounts"

    # Override save() only to log save flow for learning/debugging
    def save(self, *args, **kwargs):
        # Log before actual DB save happens
        logger.info("[MODEL] Account.save() called for email=%s", self.email)

        # Call parent save logic so Django actually writes to DB
        super().save(*args, **kwargs)

        # Log after save succeeds
        logger.info("[MODEL] Account.save() completed for id=%s", self.id)

    # Human-readable string representation of object
    def __str__(self):
        # Return email when object is printed in admin/shell/logs
        return self.email
