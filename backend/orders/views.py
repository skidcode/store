from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from django.db import transaction
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

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

        order.status = "CANCELLED"
        order.save()

        return Response({"detail": "Order cancelled"}, status=200)


# ---------------------------------------------------
# ADMIN ORDER VIEWSET
# ---------------------------------------------------


class AdminOrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin-only:
    - GET /api/orders/
    - Filtering enabled
    """

    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]

    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = OrderFilter
    ordering_fields = ["total_amount", "created_at", "status"]
