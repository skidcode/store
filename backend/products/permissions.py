from rest_framework.permissions import BasePermission, SAFE_METHODS


class ReadOnlyOrAdmin(BasePermission):
    """
    Permission class for product & category endpoints.

    Rules:
    - Anyone (even anonymous) can read (GET, HEAD, OPTIONS)
    - Only admin users can write (POST, PUT, PATCH, DELETE)
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
