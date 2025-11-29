from rest_framework.permissions import BasePermission
from .models import AUTHOR, ADMIN  # models.py से constants import करें


# 1. 👑 Admin के लिए Permission
class IsAdminOrReadOnly(BasePermission):
    """
    Allow full access only to Admin users. Others get read-only access.
    """

    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS (SAFE_METHODS) हमेशा सभी को अनुमत हैं
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # Write operations (POST, PUT, DELETE) केवल Admin के लिए अनुमत हैं
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == ADMIN
        )


# 2. ✍️ Author के लिए Permission
class IsAuthorOrReadOnly(BasePermission):
    """
    Allow full access only to Author users. Others get read-only access.
    """

    def has_permission(self, request, view):
        # GET, HEAD, OPTIONS (SAFE_METHODS) हमेशा सभी को अनुमत हैं
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # Write operations केवल Author के लिए अनुमत हैं
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == AUTHOR
        )


# 3. 🎯 Ownership Check (Method 6 का मुख्य भाग)
class IsAuthorOrAdminOrOwner(BasePermission):
    """
    Allows full access to Admin.
    Allows access to Author only if they are the owner of the object being edited.
    """

    # 🔑 List/Create Operations के लिए (सभी को List/Create करने की अनुमति किसे है)
    def has_permission(self, request, view):
        # Admin को List/Create की अनुमति
        if request.user.role == ADMIN:
            return True

        # Author को List और Create की अनुमति (बाद में Ownership चेक के लिए)
        if request.user.role == AUTHOR:
            return True

        # Basic User को केवल Read-Only (GET) की अनुमति
        return request.method in ("GET", "HEAD", "OPTIONS")

    # 🔑 Detail/Update/Delete Operations के लिए (Ownership Check)
    def has_object_permission(self, request, view, obj):
        # Admin को हमेशा पूर्ण एक्सेस (Update/Delete) की अनुमति
        if request.user.role == ADMIN:
            return True

        # Read-only methods (GET) हमेशा सभी को अनुमत हैं (Basic User, Guest)
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        # 🎯 Ownership Check: User केवल अपनी Book को ही Edit/Delete कर सकता है
        if request.user.role == AUTHOR:
            # Book का author फ़ील्ड सीधे CustomUser से जुड़ा है
            return obj.author == request.user

        # बाकियों के लिए Deny
        return False


from rest_framework import permissions
from .models import CustomUser  # Apne CustomUser model ko import karein


class IsAdminOrSelf(permissions.BasePermission):
    """
    1. Admin users ko sab kuch (list, create, update, delete) karne ki anumati de.
    2. Other users ko sirf 'apne' profile ko update/delete karne ki anumati de.
    3. Registration (POST) sabke liye open ho.
    """

    def has_permission(self, request, view):
        # Allow Registration (POST method) for everyone
        if view.action == "create":
            return True

        # Admin users ko list, retrieve, update, delete karne ki anumati de
        if request.user.is_authenticated and request.user.role == CustomUser.ADMIN:
            return True

        # Baaki users sirf apne profile ko hi dekhenge/update karenge (handled by has_object_permission)
        # LIST operation (GET /users/) sirf Admin ke liye allowed
        if view.action == "list":
            return False  # Non-admin cannot list all users

        # Agar user logged in hai to has_object_permission check karega
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin ko kisi bhi object par full permission
        if request.user.role == CustomUser.ADMIN:
            return True

        # Non-admin users sirf apne object ko edit/view kar sakte hain (Self-edit)
        # Safe methods (GET, HEAD, OPTIONS) allowed hain agar user owner hai
        if request.method in permissions.SAFE_METHODS:
            return obj == request.user

        # PUT/PATCH/DELETE sirf tab allowed jab user, object ka owner ho
        return obj == request.user
