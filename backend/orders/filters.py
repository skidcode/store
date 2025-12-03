import django_filters
from .models import Order


class OrderFilter(django_filters.FilterSet):
    """
    Filters for Order queryset.
    Useful for admin dashboards.
    """

    min_total = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="gte"
    )
    max_total = django_filters.NumberFilter(
        field_name="total_amount", lookup_expr="lte"
    )
    date_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    date_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

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
