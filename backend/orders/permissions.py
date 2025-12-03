from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrOrderOwner(BasePermission):
    """
    Custom permission class for Order access.

    Rules:
    - Admin users have full access.
    - Regular authenticated users can only access their own orders.
    """

    def has_object_permission(self, request, view, obj):
        # Admin can do anything
        if request.user.is_staff:
            return True

        # Regular users can only see their own orders
        return obj.user == request.user

    def has_permission(self, request, view):
        # Must be authenticated at least
        return request.user and request.user.is_authenticated
