from rest_framework import permissions

class ProfileOwnerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return True
    
    def has_object_permission(self, request, view, obj):
        if obj.user == request.user:
            return True
        return False