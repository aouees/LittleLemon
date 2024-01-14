from rest_framework import permissions


class IsManager(permissions.BasePermission):
    """
    Global permission check for if the user in manager group.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='manager').exists()
    
class IsDelivery(permissions.BasePermission):
    """
    Global permission check for if the user in delivery group.
    """
    def has_permission(self, request, view):
        return request.user.groups.filter(name='delivery').exists()