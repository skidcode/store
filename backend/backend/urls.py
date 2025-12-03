from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from books.views import BookViewSet, AuthorViewSet, CategoryViewSet
from orders.views import CartViewSet, OrderViewSet

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="books")
router.register(r"authors", AuthorViewSet, basename="authors")
router.register(r"categories", CategoryViewSet, basename="categories")

router.register(r"carts", CartViewSet, basename="carts")
router.register(r"orders", OrderViewSet, basename="orders")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
]
