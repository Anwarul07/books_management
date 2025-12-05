from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrAuthorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return False
        if user.role == "admin" or user.is_superuser:
            return True
        if user.role in ["author", "basic_user"] or not user.is_superuser:
            return obj.id == user.id
        return False


class UserRolepermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated or request.user.is_anonymous:
            return False
        if user.role == "admin" or user.is_superuser:
            return True
        if user.role in ["author", "basic_user"] or not user.is_superuser:
            return obj.id == user.id
        return False


class RegisterPermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if (
            not request.user.is_authenticated
            or request.user.is_anonymous
            or request.user
        ):
            if request.method in ("POST"):
                return True
            return True

    def has_object_permission(self, request, view, obj):
        return False
