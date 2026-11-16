from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Links a login account to the barangay it represents (blank for CPDO staff)."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    barangay = models.ForeignKey(
        "projects.Barangay", null=True, blank=True, on_delete=models.SET_NULL, related_name="accounts"
    )

    def __str__(self):
        return f"{self.user} ({self.barangay or 'no barangay'})"
