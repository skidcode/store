from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from products.models import Product


class CartTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", password="123456")
        self.client.login(username="test", password="123456")
        self.product = Product.objects.create(
            name="Test Product", price=1000, stock=10, slug="test-product"
        )

    def test_add_to_cart(self):
        response = self.client.post(
            "/api/cart/add/", {"product_id": self.product.id, "quantity": 2}
        )

        self.assertEqual(response.status_code, 200)
