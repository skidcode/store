from django.db import models
from django.conf import settings
from products.models import Product


class Cart(models.Model):
    """
    Represents the shopping cart of a user.

    Every user has exactly one cart (OneToOne relation). Items inside the cart
    are temporary — once an order is created, the cart is emptied.

    Fields:
        user (OneToOneField): The owner of the cart.
        created_at (DateTime): Timestamp when the cart is created.
        updated_at (DateTime): Timestamp when the cart was last modified.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart ({self.user.username})"


class CartItem(models.Model):
    """
    Represents an item inside the user's cart.

    Fields:
        cart (ForeignKey): Reference to the user's cart.
        product (ForeignKey): Product added to the cart.
        quantity (PositiveInteger): How many units of the product.
    """

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"


class Order(models.Model):
    """
    Represents a completed or in-progress order.

    Fields:
        user (ForeignKey): The user who placed the order.
        status (CharField): Status of the order (pending, paid, shipped...).
        total_amount (Decimal): Total price of the order.
        shipping_address (TextField): Address where the order is shipped.
        created_at (DateTime): Creation timestamp.
        paid_at (DateTime): Timestamp when payment is confirmed.
        stripe_session_id (CharField): Stripe Checkout session identifier.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("CANCELLED", "Cancelled"),
        ("SHIPPED", "Shipped"),
        ("DELIVERED", "Delivered"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    stripe_session_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Order #{self.id} - {self.status}"


class OrderItem(models.Model):
    """
    Represents a product inside an order.

    IMPORTANT:
    The price is stored as `unit_price` so that the order remains accurate
    even if the product price changes in the future.

    Fields:
        order (ForeignKey): Reference to the parent order.
        product (ForeignKey): Product purchased.
        quantity (PositiveInteger): Number of units purchased.
        unit_price (Decimal): Price of the product at purchase time.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} × {self.product.name} @ {self.unit_price}"
