def user_barangay(user):
    """The barangay a barangay official is registered to, or None."""
    official = getattr(user, "barangay_official", None)
    return official.barangay if official else None


def is_city_official(user):
    """City officials (and superusers) can update project status."""
    return bool(
        user.is_authenticated
        and (user.is_superuser or getattr(user, "city_official", None) is not None)
    )
