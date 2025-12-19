from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from accounts.views import RegisterViewSet
from products.views import ProductViewSet, CategoryViewSet
from orders.views import (
    CartViewSet,
    UserOrderViewSet,
    AdminOrderViewSet,
    StripeWebhookView,
)

# Routers
router = DefaultRouter()
# Auth Router
router.register(r"auth/register", RegisterViewSet, basename="register")
# Products Router
router.register(r"products", ProductViewSet)
# Categories Router
router.register(r"categories", CategoryViewSet, basename="categories")
# Admin Orders Router
admin_router = DefaultRouter()
admin_router.register(r"orders", AdminOrderViewSet, basename="admin-orders")
# User Orders Router
router.register(r"my/orders", UserOrderViewSet, basename="user-orders")
# Cart Router
router.register(r"cart", CartViewSet, basename="cart")

urlpatterns = [
    # Admin panel
    path("admin/", admin.site.urls),
    # Auth
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Routers
    path("api/", include(router.urls)),
    path("api/admin/", include(admin_router.urls)),
    path("api/payments/stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]
