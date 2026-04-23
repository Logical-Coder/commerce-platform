# Import Django test base class
from django.test import TestCase

# Import DRF API test client
from rest_framework.test import APIClient

# Import DRF status codes
from rest_framework import status

# Import Account model
from apps.accounts.models import Account


# Test class for auth APIs
class AuthAPITest(TestCase):
    # Setup runs before each test method
    def setUp(self):
        # Create reusable API client
        self.client = APIClient()

        # Test user credentials
        self.email = "test@example.com"
        self.password = "secret123"

        # Create one test account in DB
        self.user = Account.objects.create_user(
            email=self.email,
            password=self.password,
        )

    # Test successful registration
    def test_register_success(self):
        response = self.client.post(
            "/api/auth/register",
            {
                "email": "new@example.com",
                "password": "secret123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Account registered successfully")

    # Test duplicate registration
    def test_register_duplicate_email(self):
        response = self.client.post(
            "/api/auth/register",
            {
                "email": self.email,
                "password": "secret123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test successful login
    def test_login_success(self):
        response = self.client.post(
            "/api/auth/login",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    # Test wrong password login
    def test_login_wrong_password(self):
        response = self.client.post(
            "/api/auth/login",
            {
                "email": self.email,
                "password": "wrong123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)