from rest_framework import permissions

from accounts.models import User
from .models import Issue


class IsAdminRoleOrReadOnly(permissions.BasePermission):
    """
    Anyone logged in can view categories.
    Only ADMIN users can create, update, or delete categories.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == User.Role.ADMIN
        )


class IsIssueOwnerOrStaffOrAdmin(permissions.BasePermission):
    """
    Citizen can access only their own issues.
    Staff can access assigned issues.
    Admin can access all issues.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True

        if request.user.role == User.Role.STAFF:
            return obj.assigned_to == request.user

        if request.user.role == User.Role.CITIZEN:
            if request.method in permissions.SAFE_METHODS:
                return obj.reported_by == request.user

            return (
                obj.reported_by == request.user
                and obj.status == Issue.Status.PENDING
            )

        return False