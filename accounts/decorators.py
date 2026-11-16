from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def staff_required(view):
    """Log in first, then allow CPDO staff only (others get a 403 page)."""
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper
