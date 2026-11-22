from django.conf import settings
from django.db import models


class CityOfficial(models.Model):
    """CPDO / city staff. Can update the status of any project."""

    co_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="city_official")

    def __str__(self):
        return f"City official: {self.user}"


class BarangayOfficial(models.Model):
    """A user registered to one barangay using that barangay's code."""

    bo_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="barangay_official")
    barangay = models.ForeignKey("projects.Barangay", on_delete=models.PROTECT, related_name="officials")

    def __str__(self):
        return f"{self.user} ({self.barangay})"
