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

        # Verify stock status is included in product response
        self.assertEqual(response.data["results"][0]["stock_status"], "IN_STOCK")

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

    # Test admin can update product stock
    def test_admin_can_update_product_stock(self):
        # Call stock update API using admin token
        response = self.client.patch(
            f"/products/{self.product.id}/stock",
            {"stock_quantity": 100},
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
            format="json",
        )

        # Verify stock update succeeded
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify compact stock response
        self.assertEqual(response.data["id"], self.product.id)
        self.assertEqual(response.data["name"], "Sunflower Seeds")
        self.assertEqual(response.data["stock_quantity"], 100)
        self.assertEqual(response.data["stock_status"], "IN_STOCK")

        # Verify database stock value changed
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 100)

    # Test customer cannot update product stock
    def test_customer_cannot_update_product_stock(self):
        # Call stock update API using customer token
        response = self.client.patch(
            f"/products/{self.product.id}/stock",
            {"stock_quantity": 100},
            HTTP_AUTHORIZATION=f"Bearer {self.customer_token}",
            format="json",
        )

        # Verify customer is forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test anonymous user cannot update product stock
    def test_anonymous_user_cannot_update_product_stock(self):
        # Call stock update API without token
        response = self.client.patch(
            f"/products/{self.product.id}/stock",
            {"stock_quantity": 100},
            format="json",
        )

        # Verify anonymous user is forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Test stock cannot be negative
    def test_stock_update_rejects_negative_quantity(self):
        # Call stock update API with invalid negative stock
        response = self.client.patch(
            f"/products/{self.product.id}/stock",
            {"stock_quantity": -1},
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
            format="json",
        )

        # Verify validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Test stock quantity is required for stock update
    def test_stock_update_requires_stock_quantity(self):
        # Call stock update API without stock_quantity
        response = self.client.patch(
            f"/products/{self.product.id}/stock",
            {},
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
            format="json",
        )

        # Verify validation error
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("stock_quantity", response.data)

    # Test stock update returns low stock status
    def test_stock_update_returns_low_stock_status(self):
        # Call stock update API with low stock quantity
        response = self.client.patch(
            f"/products/{self.product.id}/stock",
            {"stock_quantity": 10},
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
            format="json",
        )

        # Verify low stock status in response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock_status"], "LOW_STOCK")

    # Test stock update returns out of stock status
    def test_stock_update_returns_out_of_stock_status(self):
        # Call stock update API with zero stock quantity
        response = self.client.patch(
            f"/products/{self.product.id}/stock",
            {"stock_quantity": 0},
            HTTP_AUTHORIZATION=f"Bearer {self.admin_token}",
            format="json",
        )

        # Verify out of stock status in response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["stock_status"], "OUT_OF_STOCK")

    # Test stock status values
    def test_product_stock_status_values(self):
        # Verify OUT_OF_STOCK
        self.product.stock_quantity = 0
        self.product.save()
        response = self.client.get(f"/products/{self.product.id}")
        self.assertEqual(response.data["stock_status"], "OUT_OF_STOCK")

        # Verify LOW_STOCK
        self.product.stock_quantity = 10
        self.product.save()
        response = self.client.get(f"/products/{self.product.id}")
        self.assertEqual(response.data["stock_status"], "LOW_STOCK")

        # Verify IN_STOCK
        self.product.stock_quantity = 11
        self.product.save()
        response = self.client.get(f"/products/{self.product.id}")
        self.assertEqual(response.data["stock_status"], "IN_STOCK")
