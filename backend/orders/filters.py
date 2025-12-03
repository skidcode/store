import django_filters
from .models import Order


class OrderFilter(django_filters.FilterSet):
    """
    Filters for the Order model.

    Provides advanced filtering capabilities for admin views or order listings.

    Available filters:
        - status: Filter by order status (PENDING, PAID, CANCELLED, SHIPPED)
        - user: Filter by user ID
        - min_total: Orders with total_amount >= value
        - max_total: Orders with total_amount <= value
        - date_after: Orders created on or after a given date
        - date_before: Orders created on or before a given date
    """

    min_total = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="gte", label="Minimum order total"
    )

    max_total = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="lte", label="Maximum order total"
    )

    date_after = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Created after date"
    )

    date_before = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Created before date"
    )

    class Meta:
        model = Order
        fields = [
            "status",
            "user",
            "min_total",
            "max_total",
            "date_after",
            "date_before",
        ]
