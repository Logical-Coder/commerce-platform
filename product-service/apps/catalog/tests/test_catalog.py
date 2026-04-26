# Import Django test base class
from django.test import TestCase

# Import DRF APIClient for API testing
from rest_framework.test import APIClient

# Import DRF status codes
from rest_framework import status

# Import RefreshToken to generate JWT tokens for tests
from rest_framework_simplejwt.tokens import RefreshToken

# Import catalog models
from apps.catalog.models import Category, Product


# Test cases for catalog/product APIs
class CatalogAPITest(TestCase):
    # This method runs before each test
    def setUp(self):
        # Create API client for test requests
        self.client = APIClient()

        # Create test category
        self.category = Category.objects.create(
            name="Seeds",
            slug="seeds",
            description="Healthy seeds category",
        )

        # Create test product
        self.product = Product.objects.create(
            category=self.category,
            name="Sunflower Seeds",
            slug="sunflower-seeds",
            description="Healthy sunflower seeds",
            price=120,
            stock_quantity=50,
        )

        # Create admin JWT token
        self.admin_token = self.create_token(role="ADMIN")

        # Create customer JWT token
        self.customer_token = self.create_token(role="CUSTOMER")

    # Helper method to create JWT token with role
    def create_token(self, role):
        # Create refresh token without DB user dependency
        token = RefreshToken()

        # Add fake user id
        token["user_id"] = "1"

        # Add fake email
        token["email"] = "test@example.com"

        # Add role
        token["role"] = role

        # Add active account status
        token["account_status"] = "ACTIVE"

        # Return access token as string
        return str(token.access_token)

    # Test health endpoint
    def test_health_api_success(self):
        # Call health API
        response = self.client.get("/health")

        # Verify status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify response status
        self.assertEqual(response.json()["status"], "ok")

    # Test public category list
    def test_category_list_public_access(self):
        # Call category list without token
        response = self.client.get("/categories")

        # Verify public read is allowed
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test public product list
    def test_product_list_public_access(self):
        # Call product list without token
        response = self.client.get("/products")

        # Verify public read is allowed
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # Test customer cannot create product
    def test_customer_cannot_create_product(self):
        # Call product create API using customer token
        response = self.client.post(
            "/products",
            {
                "category": self.category.id,
                "name": "Pumpkin Seeds",
                "slug": "pumpkin-seeds",
                "description": "Healthy pumpkin seeds",
                "price": 180,
                "stock_quantity": 30,
            },
            HTTP_AUTHORIZATION=f"Bearer {self.customer_token}",
            format="json",
        )

        # Verify customer is forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test admin can create product
    def test_admin_can_create_product(self):
        # Call product create API using admin token
        response = self.client.post(
            "/products",
            {
                "category": self.category.id,
                "name": "Pumpkin Seeds",
                "slug": "pumpkin-seeds",
                "description": "Healthy pumpkin seeds",
                "price": 180,
                "stock_quantity": 30,
            },
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
            format="json",
        )

        # Verify product created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify product name
        self.assertEqual(response.data["name"], "Pumpkin Seeds")

    # Test search product
    def test_product_search(self):
        # Search product by keyword
        response = self.client.get("/products?search=sunflower")

        # Verify success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify at least one result exists
        self.assertGreaterEqual(response.data["count"], 1)

    # Test product price range filter
    def test_product_price_filter(self):
        # Filter products by min and max price
        response = self.client.get("/products?min_price=100&max_price=150")

        # Verify success
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify result exists
        self.assertGreaterEqual(response.data["count"], 1)

    # Test product ordering
    def test_product_ordering(self):
        # Order products by price descending
        response = self.client.get("/products?ordering=-price")

        # Verify success
        self.assertEqual(response.status_code, status.HTTP_200_OK)
