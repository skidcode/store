from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.db import transaction
from django.db.models import F, Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

try:  # Stripe is optional; provide placeholder to allow tests without the package installed.
    import stripe  # type: ignore
except ImportError:  # pragma: no cover
    class _StripePlaceholder:
        class error:
            class SignatureVerificationError(Exception):
                ...

        class Webhook:
            @staticmethod
            def construct_event(*args, **kwargs):
                raise ImportError("stripe package not installed")

        class checkout:
            class Session:
                @staticmethod
                def create(*args, **kwargs):
                    raise ImportError("stripe package not installed")

    stripe = _StripePlaceholder()

from .permissions import IsAdmin
from .models import Cart, CartItem, Order, OrderItem
from .filters import OrderFilter
from .serializers import (
    CartSerializer,
    CreateOrderSerializer,
    OrderSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)
from products.models import Product


# ---------------------------------------------------
# CART VIEWSET
# ---------------------------------------------------


class CartViewSet(viewsets.ViewSet):
    """
    Handles everything related to the authenticated user's cart.

    Routes generated:
    - GET    /api/cart/             → get cart
    - POST   /api/cart/add/         → add item
    - PATCH  /api/cart/item/<id>/   → update quantity
    - DELETE /api/cart/item/<id>/   → remove item
    """

    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Return user's cart"""
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=["post"])
    def add(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = Product.objects.get(id=serializer.validated_data["product_id"])
        quantity = serializer.validated_data["quantity"]

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        new_quantity = quantity if created else item.quantity + quantity

        if new_quantity > product.stock:
            return Response(
                {
                    "detail": "Not enough stock available",
                    "available_stock": product.stock,
                },
                status=400,
            )

        item.quantity = new_quantity
        item.save()

        return Response({"detail": "Added to cart"}, status=200)

    @action(detail=True, methods=["patch"], url_path="update")
    def update_item(self, request, pk=None):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            item = CartItem.objects.get(id=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=404)

        new_quantity = serializer.validated_data["quantity"]

        if new_quantity > item.product.stock:
            return Response(
                {
                    "detail": "Not enough stock available",
                    "available_stock": item.product.stock,
                },
                status=400,
            )

        item.quantity = new_quantity
        item.save()

        return Response({"detail": "Quantity updated"}, status=200)

    @action(detail=True, methods=["delete"], url_path="remove")
    def remove_item(self, request, pk=None):
        try:
            item = CartItem.objects.get(id=pk, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=404)

        item.delete()
        return Response({"detail": "Item removed"}, status=200)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()
        return Response({"detail": "Cart cleared"}, status=200)


# ---------------------------------------------------
# USER ORDER VIEWSET
# ---------------------------------------------------


class UserOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    User endpoint:
    - GET /api/my/orders/ → list user's orders
    - POST /api/my/orders/create/ → create order from cart
    - POST /api/my/orders/<id>/cancel/ → cancel order
    """

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ["total_amount", "created_at", "status"]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")

    @action(detail=False, methods=["post"])
    def create_order(self, request):
        user = request.user

        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipping_address = serializer.validated_data["shipping_address"]

        try:
            with transaction.atomic():
                cart = Cart.objects.select_for_update().get(user=user)
                cart_items = list(
                    cart.items.select_related("product").select_for_update()
                )

                if not cart_items:
                    return Response({"detail": "Cart is empty"}, status=400)

                product_ids = [item.product_id for item in cart_items]
                products = Product.objects.select_for_update().filter(
                    id__in=product_ids
                )
                stock_by_product = {product.id: product.stock for product in products}

                for item in cart_items:
                    available = stock_by_product.get(item.product_id, 0)
                    if item.quantity > available:
                        return Response(
                            {
                                "detail": "Not enough stock available",
                                "product": item.product.name,
                                "available_stock": available,
                            },
                            status=400,
                        )

                total = sum(item.product.price * item.quantity for item in cart_items)

                order = Order.objects.create(
                    user=user,
                    status="PENDING",
                    total_amount=total,
                    shipping_address=shipping_address,
                )

                for item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        unit_price=item.product.price,
                    )
                    Product.objects.filter(id=item.product_id).update(
                        stock=F("stock") - item.quantity
                    )

                cart.items.all().delete()

            return Response(OrderSerializer(order).data, status=201)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart does not exist"}, status=400)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()

        if order.status != "PENDING":
            return Response(
                {"detail": "Only PENDING orders can be cancelled"}, status=400
            )

        with transaction.atomic():
            # return stock to inventory
            for item in order.items.select_related("product"):
                Product.objects.filter(id=item.product_id).update(
                    stock=F("stock") + item.quantity
                )

            order.status = "CANCELLED"
            order.save()

        return Response({"detail": "Order cancelled"}, status=200)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        """
        Create a Stripe Checkout session for this order.
        """

        order = self.get_object()

        if order.status != "PENDING":
            return Response(
                {"detail": "Only PENDING orders can be paid"}, status=400
            )

        if not settings.STRIPE_SECRET_KEY:
            return Response(
                {"detail": "Stripe is not configured (missing STRIPE_SECRET_KEY)"},
                status=500,
            )

        stripe.api_key = settings.STRIPE_SECRET_KEY

        success_url = request.data.get("success_url")
        cancel_url = request.data.get("cancel_url")

        if not success_url or not cancel_url:
            base = request.build_absolute_uri("/").rstrip("/")
            success_url = success_url or f"{base}/checkout/success"
            cancel_url = cancel_url or f"{base}/checkout/cancel"

        line_items = []
        for item in order.items.select_related("product"):
            unit_amount = int(item.unit_price * 100)
            line_items.append(
                {
                    "quantity": item.quantity,
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": unit_amount,
                        "product_data": {"name": item.product.name},
                    },
                }
            )

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                mode="payment",
                line_items=line_items,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={"order_id": order.id},
            )
        except ImportError:
            return Response(
                {"detail": "Stripe SDK not installed. Run `pip install stripe`."},
                status=500,
            )

        order.stripe_session_id = session.id
        order.save(update_fields=["stripe_session_id"])

        return Response(
            {"checkout_url": session.url, "session_id": session.id}, status=200
        )


# ---------------------------------------------------
# ADMIN ORDER VIEWSET
# ---------------------------------------------------


class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin-only:
    - GET /api/orders/
    - Filtering enabled
    - Change order status
    - Basic sales report
    """

    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ["total_amount", "created_at", "status"]

    @action(detail=True, methods=["post"], url_path="set-status")
    def set_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get("status")

        valid_statuses = dict(Order.STATUS_CHOICES).keys()
        if new_status not in valid_statuses:
            return Response(
                {"detail": f"Invalid status. Allowed: {', '.join(valid_statuses)}"},
                status=400,
            )

        old_status = order.status

        with transaction.atomic():
            if old_status != "CANCELLED" and new_status == "CANCELLED":
                # return stock to inventory once
                for item in order.items.select_related("product"):
                    Product.objects.filter(id=item.product_id).update(
                        stock=F("stock") + item.quantity
                    )

            order.status = new_status

            if new_status == "PAID" and not order.paid_at:
                order.paid_at = order.paid_at or timezone.now()

            order.save()

        return Response({"detail": "Status updated", "status": order.status})

    @action(detail=False, methods=["get"], url_path="report")
    def report(self, request):
        """
        Basic sales report for admins.

        Returns:
        - total_orders
        - total_revenue
        - orders_by_status
        - revenue_by_day (last 30 days)
        """

        queryset = self.filter_queryset(self.get_queryset())

        total_orders = queryset.count()
        total_revenue = queryset.aggregate(total=Sum("total_amount"))["total"] or 0

        orders_by_status = (
            queryset.values("status")
            .annotate(count=Count("id"), revenue=Sum("total_amount"))
            .order_by("status")
        )

        revenue_by_day = (
            queryset.filter(status="PAID")
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(revenue=Sum("total_amount"), orders=Count("id"))
            .order_by("-day")[:30]
        )

        return Response(
            {
                "total_orders": total_orders,
                "total_revenue": total_revenue,
                "orders_by_status": list(orders_by_status),
                "revenue_by_day": list(revenue_by_day),
            }
        )


class StripeWebhookView(APIView):
    """
    Handles Stripe webhook events.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def post(self, request):
        webhook_secret = settings.STRIPE_WEBHOOK_SECRET

        if not webhook_secret:
            return Response(
                {"detail": "Webhook secret not configured"},
                status=500,
            )

        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError:
            return Response(status=400)
        except stripe.error.SignatureVerificationError:
            return Response(status=400)
        except ImportError:
            return Response(
                {"detail": "Stripe SDK not installed. Run `pip install stripe`."},
                status=500,
            )

        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            order_id = session.get("metadata", {}).get("order_id")
            if order_id:
                with transaction.atomic():
                    try:
                        order = Order.objects.select_for_update().get(id=order_id)
                    except Order.DoesNotExist:
                        return Response(status=200)

                    if order.status != "PAID":
                        order.status = "PAID"
                        order.paid_at = order.paid_at or timezone.now()
                        order.stripe_session_id = session.get(
                            "id", order.stripe_session_id
                        )
                        order.save(update_fields=["status", "paid_at", "stripe_session_id"])

        return Response(status=200)
