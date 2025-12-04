from django.contrib import admin
from .models import Product, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "price", "stock", "category", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "description", "sku")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}
