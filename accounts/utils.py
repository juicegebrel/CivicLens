def user_barangay(user):
    """The barangay linked to a user's profile, or None."""
    return getattr(getattr(user, "profile", None), "barangay", None)
