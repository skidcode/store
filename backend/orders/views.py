from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

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

        item.quantity = item.quantity + quantity if not created else quantity
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

        item.quantity = serializer.validated_data["quantity"]
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

        # Load cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart does not exist"}, status=400)

        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty"}, status=400)

        # Compute total
        total = sum(item.product.price * item.quantity for item in cart.items.all())

        # Create order
        order = Order.objects.create(
            user=user,
            status="PENDING",
            total_amount=total,
            shipping_address=shipping_address,
        )

        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.price,
            )

        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=201)

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
