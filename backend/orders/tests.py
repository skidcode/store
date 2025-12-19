from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from products.models import Product
from orders.models import Order, OrderItem, Cart, CartItem

User = get_user_model()


class CartAndOrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user", password="123456")
        self.admin = User.objects.create_user(
            username="admin", password="admin123", is_staff=True
        )

        self.product = Product.objects.create(
            name="Test Product", price=100, stock=5, slug="test-product"
        )

    def authenticate(self, user=None):
        self.client.force_authenticate(user or self.user)

    def test_add_to_cart_respects_stock(self):
        self.authenticate()
        # quantity within stock
        ok_resp = self.client.post(
            "/api/cart/add/", {"product_id": self.product.id, "quantity": 3}
        )
        self.assertEqual(ok_resp.status_code, 200)

        # exceeding stock should fail
        fail_resp = self.client.post(
            "/api/cart/add/", {"product_id": self.product.id, "quantity": 10}
        )
        self.assertEqual(fail_resp.status_code, 400)
        self.assertIn("available_stock", fail_resp.data)

    def test_update_cart_item_respects_stock(self):
        self.authenticate()
        # add one item
        add_resp = self.client.post(
            "/api/cart/add/", {"product_id": self.product.id, "quantity": 1}
        )
        self.assertEqual(add_resp.status_code, 200)

        item = CartItem.objects.get(cart__user=self.user, product=self.product)
        # attempt to update beyond stock
        resp = self.client.patch(
            f"/api/cart/{item.id}/update/", {"quantity": 6}, format="json"
        )
        self.assertEqual(resp.status_code, 400)
        self.assertIn("available_stock", resp.data)

    def test_create_order_deducts_and_cancel_restores_stock(self):
        self.authenticate()
        # add 3 units to cart
        self.client.post(
            "/api/cart/add/", {"product_id": self.product.id, "quantity": 3}
        )

        create_resp = self.client.post(
            "/api/my/orders/create_order/",
            {"shipping_address": "123 Street"},
            format="json",
        )
        self.assertEqual(create_resp.status_code, 201)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 2)

        order_id = create_resp.data["id"]
        # cancel should restore stock to original 5
        cancel_resp = self.client.post(f"/api/my/orders/{order_id}/cancel/")
        self.assertEqual(cancel_resp.status_code, 200)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_admin_set_status_cancel_restocks_once(self):
        # create an order manually in PAID with reduced stock
        cart = Cart.objects.create(user=self.user)
        item = CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        self.authenticate()
        self.client.post(
            "/api/my/orders/create_order/",
            {"shipping_address": "123 Street"},
            format="json",
        )
        order = Order.objects.first()

        # simulate already paid by changing status without restocking
        order.status = "PAID"
        order.save()
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        # admin cancels -> restock to 5
        self.authenticate(self.admin)
        resp = self.client.post(f"/api/admin/orders/{order.id}/set-status/", {"status": "CANCELLED"})
        self.assertEqual(resp.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

        # cancelling again should NOT restock further
        resp_second = self.client.post(f"/api/admin/orders/{order.id}/set-status/", {"status": "CANCELLED"})
        self.assertEqual(resp_second.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_admin_report_structure(self):
        self.authenticate(self.admin)
        resp = self.client.get("/api/admin/orders/report/")
        self.assertEqual(resp.status_code, 200)
        for key in ["total_orders", "total_revenue", "orders_by_status", "revenue_by_day"]:
            self.assertIn(key, resp.data)
