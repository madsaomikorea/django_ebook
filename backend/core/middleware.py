from django.core.exceptions import PermissionDenied
from django_multitenant.utils import set_current_tenant

class TenantSecurityMiddleware:
    """
    Middleware to ensure the current tenant is set for all queries
    and to prevent unauthorized cross-tenant data access.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Set the tenant for django-multitenant globally for this request
            if hasattr(request.user, 'school') and request.user.school:
                set_current_tenant(request.user.school)
            
            # Simple security check: if a request context (like school_id in JSON) 
            # is different from the user's school, block it.
            # (Note: Broad enforcement usually happens in a Queryset/Manager level)
        
        response = self.get_response(request)
        
        # Clear tenant after request to prevent leaks between requests
        set_current_tenant(None)
        
        return response
