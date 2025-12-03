from rest_framework import viewsets
from rest_framework.permissions import SAFE_METHODS, BasePermission
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer
from .filters import ProductFilter
from .permissions import ReadOnlyOrAdmin


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet that handles CRUD operations for Products.

    Features:
    - Read-only for regular users.
    - Full CRUD access for admin users.
    - Supports filtering (price, stock, category).
    - Supports searching by name or description.
    - Supports ordering (name, price, stock).
    - Pagination is applied globally through DRF settings.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [ReadOnlyOrAdmin]

    # Enable filters, search and ordering
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "description"]
    ordering_fields = ["price", "stock", "name"]
    ordering = ["name"]


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet that handles CRUD operations for Categories.

    Features:
    - Read-only for regular users.
    - Full access for admin users.
    - Supports searching by category name.
    - Supports ordering alphabetically.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnlyOrAdmin]

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name"]
    ordering_fields = ["name"]
    ordering = ["name"]
