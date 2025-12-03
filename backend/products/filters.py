import django_filters
from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Filters for the Product queryset.

    Available filters:
    - min_price: filters products with price >= value
    - max_price: filters products with price <= value
    - min_stock: filters products with stock >= value
    - category: filters by category slug (case-insensitive)

    These filters allow flexible querying for the admin panel or
    frontend product list pages.
    """

    name = django_filters.CharFilter(
        field_name="name", lookup_expr="icontains", label="Product name contains"
    )
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    min_stock = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    category = django_filters.CharFilter(
        field_name="category__slug", lookup_expr="iexact"
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "category",
            "min_price",
            "max_price",
            "min_stock",
        ]
