from rest_framework import permissions

class IsAuthenticatedOrCreateOnly(permissions.BasePermission):
    """
    Global permissions to restrict access with GET, PUT and DELETE methods
    to authenticated users
    """
    _safe_methods = ['HEAD', 'OPTIONS', 'POST']
    
    def has_permission(self, request, view):
        if request.method in self._safe_methods:
            return True
        return request.user.is_authenticated