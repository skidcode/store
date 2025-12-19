from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase
from unittest.mock import patch

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

    def test_create_order_keeps_stock_until_paid(self):
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
        # Stock is not deducted until payment
        self.assertEqual(self.product.stock, 5)

        order_id = create_resp.data["id"]
        # cancel should not change stock
        cancel_resp = self.client.post(f"/api/my/orders/{order_id}/cancel/")
        self.assertEqual(cancel_resp.status_code, 200)

        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_admin_set_status_paid_and_cancel_restocks_once(self):
        self.authenticate()
        self.client.post(
            "/api/cart/add/", {"product_id": self.product.id, "quantity": 2}
        )
        create_resp = self.client.post(
            "/api/my/orders/create_order/",
            {"shipping_address": "123 Street"},
            format="json",
        )
        order = Order.objects.get(id=create_resp.data["id"])

        # admin marks as PAID -> deduct stock
        self.authenticate(self.admin)
        resp_paid = self.client.post(
            f"/api/admin/orders/{order.id}/set-status/", {"status": "PAID"}
        )
        self.assertEqual(resp_paid.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        # admin cancels -> restock
        resp_cancel = self.client.post(
            f"/api/admin/orders/{order.id}/set-status/", {"status": "CANCELLED"}
        )
        self.assertEqual(resp_cancel.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

        # cancelling again should NOT restock further
        resp_cancel_again = self.client.post(
            f"/api/admin/orders/{order.id}/set-status/", {"status": "CANCELLED"}
        )
        self.assertEqual(resp_cancel_again.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_admin_report_structure(self):
        self.authenticate(self.admin)
        resp = self.client.get("/api/admin/orders/report/")
        self.assertEqual(resp.status_code, 200)
        for key in ["total_orders", "total_revenue", "orders_by_status", "revenue_by_day"]:
            self.assertIn(key, resp.data)

    @override_settings(STRIPE_SECRET_KEY="sk_test_dummy")
    @patch("orders.views.stripe.checkout.Session.create")
    def test_pay_creates_stripe_session(self, mock_create):
        self.authenticate()
        self.client.post(
            "/api/cart/add/", {"product_id": self.product.id, "quantity": 1}
        )
        create_resp = self.client.post(
            "/api/my/orders/create_order/",
            {"shipping_address": "123 Street"},
            format="json",
        )
        order_id = create_resp.data["id"]

        mock_create.return_value = type(
            "Session", (), {"id": "cs_test_123", "url": "https://stripe.test/session"}
        )()

        pay_resp = self.client.post(
            f"/api/my/orders/{order_id}/pay/",
            {
                "success_url": "https://example.com/success",
                "cancel_url": "https://example.com/cancel",
            },
            format="json",
        )

        self.assertEqual(pay_resp.status_code, 200)
        self.assertEqual(pay_resp.data["session_id"], "cs_test_123")
        mock_create.assert_called_once()

    @override_settings(STRIPE_WEBHOOK_SECRET="whsec_test_dummy")
    @patch("orders.views.stripe.Webhook.construct_event")
    def test_webhook_marks_order_paid(self, mock_construct_event):
        self.authenticate()
        self.client.post(
            "/api/cart/add/", {"product_id": self.product.id, "quantity": 1}
        )
        create_resp = self.client.post(
            "/api/my/orders/create_order/",
            {"shipping_address": "123 Street"},
            format="json",
        )
        order_id = create_resp.data["id"]
        order = Order.objects.get(id=order_id)

        mock_construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_test_123", "metadata": {"order_id": order_id}}},
        }

        resp = self.client.post(
            "/api/payments/stripe/webhook/",
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="dummy",
        )

        self.assertEqual(resp.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.status, "PAID")
        self.assertEqual(order.stripe_session_id, "cs_test_123")
        self.assertIsNotNone(order.paid_at)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 4)
