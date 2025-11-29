from rest_framework.permissions import BasePermission, SAFE_METHODS


# -----------------------------
# 1. ADMIN PERMISSION
# -----------------------------
class IsAdmin(BasePermission):
    """
    Admin = full access everywhere.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"


# -----------------------------
# 2. AUTHOR PERMISSIONS
# -----------------------------
class IsAuthorSelfOrReadOnly(BasePermission):
    """
    Author:
    - Can view own profile
    - Can update own profile
    - Cannot modify other authors
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin always allowed
        if user.role == "ADMIN":
            return True

        # Only author
        if user.role != "AUTHOR":
            return False

        # Author can edit ONLY their own author profile
        if request.method in SAFE_METHODS:
            return True

        return obj.user == user


class IsAuthorOfBookOrReadOnly(BasePermission):
    """
    Authors:
    - Full CRUD only on their own books
    - Can GET other authors' books
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin always allowed
        if user.role == "ADMIN":
            return True

        # Unauthenticated = block
        if not user.is_authenticated:
            return request.method in SAFE_METHODS

        # Author
        if user.role == "AUTHOR":
            if request.method in SAFE_METHODS:
                return True
            return obj.author == user

        # Buyers: only read
        return request.method in SAFE_METHODS


# -----------------------------
# 3. BUYER PERMISSION (Basic User)
# -----------------------------
class IsCartOwner(BasePermission):
    """
    Buyer:
    - Can access only own cart
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Admin always allowed
        if user.role == "ADMIN":
            return True

        # Buyer access only their own cart
        return obj.user == user


# -----------------------------
# 4. READ-ONLY FOR EVERYONE ELSE
# -----------------------------
class ReadOnly(BasePermission):
    """
    Everyone else only gets GET access.
    """

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
