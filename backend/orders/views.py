from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsAdminOrOrderOwner
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
# CART
# ---------------------------------------------------


class CartView(APIView):
    """
    Retrieves the cart for the authenticated user.
    Cart is created automatically if missing.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(CartSerializer(cart).data)


class AddToCartView(APIView):
    """
    Adds a product to the user's cart or increases quantity.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = Product.objects.get(id=serializer.validated_data["product_id"])
        quantity = serializer.validated_data["quantity"]

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if created:
            item.quantity = quantity
        else:
            item.quantity += quantity

        item.save()

        return Response({"detail": "Added to cart"}, status=200)


class UpdateCartItemView(APIView):
    """
    Updates the quantity of a specific item in the user's cart.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, item_id):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=404)

        item.quantity = serializer.validated_data["quantity"]
        item.save()

        return Response({"detail": "Quantity updated"}, status=200)


class RemoveCartItemView(APIView):
    """
    Removes an item from the user's cart.
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=404)

        item.delete()
        return Response({"detail": "Item removed"}, status=200)


# ---------------------------------------------------
# ORDERS
# ---------------------------------------------------


class CreateOrderView(APIView):
    """
    Creates an order from the user's cart.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipping_address = serializer.validated_data["shipping_address"]

        # Get user cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart does not exist"}, status=400)

        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty"}, status=400)

        # Compute total
        total = sum(item.product.price * item.quantity for item in cart.items.all())

        # Create Order
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

        # Clear cart
        cart.items.all().delete()

        return Response(OrderSerializer(order).data, status=201)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only access to orders.

    - Regular users only see *their own orders*.
    - Admins can see *all* orders.
    - Supports advanced filtering.
    """

    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAdminOrOrderOwner]

    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter


class CancelOrderView(APIView):
    """
    Allows a user to cancel their own order (if still PENDING).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found"}, status=404)

        if order.status != "PENDING":
            return Response(
                {"detail": "Only PENDING orders can be cancelled"}, status=400
            )

        order.status = "CANCELLED"
        order.save()

        return Response({"detail": "Order cancelled"}, status=200)
