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

    # Test login with non-existing account
    # Test login with non-existing account
    def test_login_user_not_found(self):
        response = self.client.post(
            "/api/auth/login",
            {"email": "notfound@example.com", "password": "secret123"},
            format="json",
        )

        self.assertEqual(response.status_code, 401)

    # Test register with missing fields
    def test_register_invalid_data(self):
        response = self.client.post("/api/auth/register", {}, format="json")

        self.assertEqual(response.status_code, 400)

    # Test login missing password
    def test_login_missing_password(self):
        response = self.client.post(
            "/api/auth/login", {"email": self.email}, format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_health_success(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_health_db_success(self):
        response = self.client.get("/health/db")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["database"], "mysql")

    def test_health_redis_success(self):
        response = self.client.get("/health/redis")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["redis"], "connected")

    def test_login_inactive_account(self):
        self.user.account_status = "INACTIVE"
        self.user.save()

        response = self.client.post(
            "/api/auth/login",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["detail"], "Account is not active")


def test_me_api_success(self):
    login_response = self.client.post(
        "/api/auth/login",
        {
            "email": self.email,
            "password": self.password,
        },
        format="json",
    )

    access_token = login_response.data["access"]

    response = self.client.get(
        "/api/auth/me",
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data["email"], self.email)


def test_me_api_without_token(self):
    response = self.client.get("/api/auth/me")

    self.assertEqual(response.status_code, 401)


def test_customer_cannot_access_admin_api(self):
    login_response = self.client.post(
        "/api/auth/login",
        {
            "email": self.email,
            "password": self.password,
        },
        format="json",
    )

    access_token = login_response.data["access"]

    response = self.client.get(
        "/api/auth/admin-only",
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )

    self.assertEqual(response.status_code, 403)


def test_admin_can_access_admin_api(self):
    admin = Account.objects.create_user(
        email="admin@example.com",
        password="admin123",
        role="ADMIN",
        is_staff=True,
        is_superuser=True,
    )

    login_response = self.client.post(
        "/api/auth/login",
        {
            "email": admin.email,
            "password": "admin123",
        },
        format="json",
    )

    access_token = login_response.data["access"]

    response = self.client.get(
        "/api/auth/admin-only",
        HTTP_AUTHORIZATION=f"Bearer {access_token}",
    )

    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.data["role"], "ADMIN")
