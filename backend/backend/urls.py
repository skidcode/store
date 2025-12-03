from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from accounts.views import register
from products.views import ProductViewSet, CategoryViewSet
from orders.views import (
    CartViewSet,
    CreateOrderView,
    OrderViewSet,
    CartView,
    AddToCartView,
    UpdateCartItemView,
    RemoveCartItemView,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet)
router.register(r"product-categories", CategoryViewSet)
router.register(r"categories", CategoryViewSet, basename="categories")

router.register(r"carts", CartViewSet, basename="carts")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth
    path("api/auth/register/", register, name="register"),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Cart
    path("api/cart/", CartView.as_view(), name="cart"),
    path("api/cart/add/", AddToCartView.as_view(), name="cart_add"),
    path(
        "api/cart/item/<int:item_id>/update/",
        UpdateCartItemView.as_view(),
        name="cart_item_update",
    ),
    path(
        "api/cart/item/<int:item_id>/remove/",
        RemoveCartItemView.as_view(),
        name="cart_item_remove",
    ),
    path("api/orders/create/", CreateOrderView.as_view(), name="order_create"),
    # API
    path("api/", include(router.urls)),
]
