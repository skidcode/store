from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOrderOwner(BasePermission):
    """
    Allows access only to the owner of the order.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
