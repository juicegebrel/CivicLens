from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .utils import is_city_official


def city_official_required(view):
    """Log in first, then allow city officials only (others get a 403 page)."""
    @login_required
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not is_city_official(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapper
