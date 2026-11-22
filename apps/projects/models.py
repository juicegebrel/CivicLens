import re
import secrets

from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Status(models.TextChoices):
    APPROVED = "approved", "Approved"
    BIDDING = "bidding", "In bidding"
    AWARDED = "awarded", "Awarded"
    IN_PROCESS = "in_process", "In process"
    COMPLETED = "completed", "Completed"
    ON_HOLD = "on_hold", "On hold"
    CANCELLED = "cancelled", "Cancelled"


# One colour per status, shared by the infographics and the badges.
STATUS_COLORS = {
    "approved": "#8793a6",
    "bidding": "#7a5cc2",
    "awarded": "#2a8fbd",
    "in_process": "#e0a100",
    "completed": "#2b8a57",
    "on_hold": "#cf5a3f",
    "cancelled": "#4e5964",
}

# Projects in these statuses have started drawing on their allocated funds.
COMMITTED_STATUSES = (Status.AWARDED, Status.IN_PROCESS, Status.COMPLETED)

# No 0/O or 1/I/L, so codes are easy to read out and type.
CODE_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"


def generate_barangay_code():
    """Random, unique registration code such as 'K7M2-QX9T'."""
    while True:
        raw = "".join(secrets.choice(CODE_ALPHABET) for _ in range(8))
        code = f"{raw[:4]}-{raw[4:]}"
        if not Barangay.objects.filter(barangay_code=code).exists():
            return code


class Barangay(models.Model):
    barangay_id = models.AutoField(primary_key=True)
    barangay_name = models.CharField(max_length=50, unique=True)
    barangay_code = models.CharField(
        max_length=50, unique=True, default=generate_barangay_code,
        help_text="Give this code to the barangay's officials so they can register.",
    )

    class Meta:
        ordering = ["barangay_name"]

    def __str__(self):
        return self.barangay_name

    def regenerate_code(self):
        self.barangay_code = generate_barangay_code()
        self.save(update_fields=["barangay_code"])


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.APPROVED)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    project_date = models.DateField(default=timezone.localdate)
    barangays = models.ManyToManyField(Barangay, through="BarangayProject", related_name="projects")

    class Meta:
        ordering = ["-project_date", "-project_id"]

    def __str__(self):
        return f"{self.code} {self.project_name}"

    def get_absolute_url(self):
        return reverse("project_detail", args=[self.code])

    @property
    def code(self):
        """Public reference code derived from the primary key, e.g. LDF-0042."""
        return f"LDF-{self.pk:04d}" if self.pk else ""

    @staticmethod
    def pk_from_code(code):
        match = re.match(r"^(?:LDF-)?0*(\d+)$", (code or "").strip(), re.IGNORECASE)
        return int(match.group(1)) if match else None


class BarangayProject(models.Model):
    """Which barangay a project serves, and the sitio (purok/area) within it."""

    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE, related_name="project_links")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="barangay_links")
    sitio = models.CharField(max_length=50, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["barangay", "project"], name="unique_barangay_project"),
        ]

    def __str__(self):
        return f"{self.project.project_name} @ {self.barangay}"
