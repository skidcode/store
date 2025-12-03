from rest_framework import serializers

from .models import Cart, CartItem, Order, OrderItem
from products.models import Product
from products.serializers import ProductSerializer


class AddToCartSerializer(serializers.Serializer):
    """
    Serializer used when adding a product to the user's cart.

    Fields:
        product_id (int): ID of the product to add.
        quantity (int): Quantity to add. Defaults to 1.

    Validations:
        - Ensures the product exists.
    """

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

    def validate_product_id(self, value):
        """Ensure the provided product exists."""
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Product not found")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    """
    Serializer used to update the quantity of a cart item.

    Fields:
        quantity (int): New quantity for the item.
    """

    quantity = serializers.IntegerField()


class CartItemSerializer(serializers.ModelSerializer):
    """
    Represents a single item inside the user's cart.

    Provides nested product information using ProductSerializer.
    """

    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    """
    Represents the user's entire shopping cart.

    Includes:
        - User's cart metadata.
        - A list of cart items via CartItemSerializer.
    """

    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Represents a single item inside an order.

    Includes:
        - Product snapshot (via ProductSerializer)
        - Quantity
        - Unit price at time of purchase
    """

    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    """
    Represents a complete order.

    Includes:
        - Order metadata
        - List of order items (OrderItemSerializer)
    """

    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"


class CreateOrderSerializer(serializers.Serializer):
    """
    Serializer used when creating a new order.

    Fields:
        shipping_address (str): Address where the order will be delivered.

    Notes:
        - The order total, items, and user are handled by the view logic.
    """

    shipping_address = serializers.CharField()
