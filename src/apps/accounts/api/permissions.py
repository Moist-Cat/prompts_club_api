from rest_framework.permissions import BasePermission

class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        user = obj.pk
        if user == request.user.pk:
            return True
        return False
