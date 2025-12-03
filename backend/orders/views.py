from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import status

from .filters import OrderFilter
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer,
    CreateOrderSerializer,
    OrderSerializer,
    AddToCartSerializer,
    UpdateCartItemSerializer,
)
from products.models import Product

# ---------------------------------------------------------
#   CART VIEWS
# ---------------------------------------------------------


class CartView(APIView):
    """
    GET /api/cart/
    Returns the authenticated user's cart.
    If it does not exist, it will be created automatically.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddToCartView(APIView):
    """
    POST /api/cart/add/
    Adds a product to the authenticated user's cart.

    Body:
    {
        "product_id": int,
        "quantity": int
    }

    If the item already exists, its quantity is increased.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = Product.objects.get(id=serializer.validated_data["product_id"])
        quantity = serializer.validated_data["quantity"]

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity

        item.save()

        return Response({"detail": "Added to cart"}, status=200)


class UpdateCartItemView(APIView):
    """
    PATCH /api/cart/item/<item_id>/update/
    Updates the quantity of a cart item.

    Body:
    {
        "quantity": int
    }

    Errors:
    - 404 if item does not exist or does not belong to the user
    """

    permission_classes = [IsAuthenticated]

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
    DELETE /api/cart/item/<item_id>/remove/
    Removes a product from the authenticated user's cart.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = CartItem.objects.get(id=item_id, cart__user=request.user)
        except CartItem.DoesNotExist:
            return Response({"detail": "Item not found"}, status=404)

        item.delete()
        return Response({"detail": "Item removed"}, status=200)


# ---------------------------------------------------------
#   ORDER VIEWS
# ---------------------------------------------------------


class CreateOrderView(APIView):
    """
    POST /api/orders/create/
    Creates an order using the authenticated user's cart.

    Body:
    {
        "shipping_address": string
    }

    Steps:
    1. Validate shipping data
    2. Get user's cart
    3. Validate that the cart is not empty
    4. Calculate total
    5. Create order
    6. Create OrderItems snapshot
    7. Clear the cart

    Returns:
    - Order data (JSON)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        shipping_address = serializer.validated_data["shipping_address"]

        # Retrieve cart
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response({"detail": "Cart does not exist"}, status=400)

        if cart.items.count() == 0:
            return Response({"detail": "Cart is empty"}, status=400)

        # Calculate total
        total = sum(item.product.price * item.quantity for item in cart.items.all())

        # Create order
        order = Order.objects.create(
            user=user,
            status="PENDING",
            total_amount=total,
            shipping_address=shipping_address,
        )

        # Create order items snapshot
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


class ListOrdersView(APIView):
    """
    GET /api/orders/
    Returns all orders belonging to the authenticated user.
    Ordered by creation date (newest first).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=200)


class CancelOrderView(APIView):
    """
    POST /api/orders/<order_id>/cancel/
    Cancels the order IF:
    - It belongs to the authenticated user
    - Its status is 'PENDING'

    Errors:
    - 404: order not found
    - 400: cannot cancel non-pending orders
    """

    permission_classes = [IsAuthenticated]

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


class ListAllOrdersView(APIView):
    """
    GET /api/admin/orders/
    ADMIN ONLY

    Returns all orders in the system.
    (Note: Filters are configured but APIView does not apply them automatically)

    Recommended improvement:
    Convert to ListAPIView for full filter support.
    """

    queryset = Order.objects.all().order_by("-created_at")
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    filterset_class = OrderFilter
