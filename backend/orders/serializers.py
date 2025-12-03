from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from books.serializers import BookSerializer
from books.models import Book


class AddToCartSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(default=1)

    def validate_book_id(self, value):
        if not Book.objects.filter(id=value).exists():
            raise serializers.ValidationError("Book not found")
        return value


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField()


class CartItemSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = "__all__"


class OrderItemSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
