import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
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


# One colour per status, shared by the infographics and the badges (see civiclens.css).
STATUS_COLORS = {
    "approved": "#8793a6",
    "bidding": "#7a5cc2",
    "awarded": "#2a8fbd",
    "in_process": "#e0a100",
    "completed": "#2b8a57",
    "on_hold": "#cf5a3f",
    "cancelled": "#4e5964",
}


def current_year():
    return timezone.localdate().year


class Barangay(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Project(models.Model):
    code = models.CharField("reference code", max_length=24, unique=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    barangay = models.ForeignKey(Barangay, on_delete=models.PROTECT, related_name="projects")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="projects")
    fiscal_year = models.PositiveIntegerField(default=current_year)
    budget = models.DecimalField("approved budget (PHP)", max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPROVED)
    progress_percent = models.PositiveSmallIntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    start_date = models.DateField(null=True, blank=True)
    target_end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.code} {self.title}"

    def get_absolute_url(self):
        return reverse("project_detail", args=[self.code])

    @property
    def is_overdue(self):
        return bool(
            self.target_end_date
            and self.target_end_date < timezone.localdate()
            and self.status not in (Status.COMPLETED, Status.CANCELLED)
        )

    def save(self, *args, **kwargs):
        needs_code = not self.code
        if needs_code:
            self.code = "TMP-" + uuid.uuid4().hex[:12]
        super().save(*args, **kwargs)
        if needs_code:
            self.code = f"LDF-{self.fiscal_year}-{self.pk:04d}"
            super().save(update_fields=["code"])

    def apply_update(self, status, progress, remarks="", user=None):
        """Record a status change in the history and sync the project's current state."""
        if status == Status.COMPLETED:
            progress = 100
        with transaction.atomic():
            update = StatusUpdate.objects.create(
                project=self, status=status, progress_percent=progress, remarks=remarks, updated_by=user
            )
            self.status = status
            self.progress_percent = progress
            self.save(update_fields=["status", "progress_percent", "updated_at"])
        return update


class StatusUpdate(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="updates")
    status = models.CharField(max_length=20, choices=Status.choices)
    progress_percent = models.PositiveSmallIntegerField(default=0)
    remarks = models.TextField(blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.project.code}: {self.get_status_display()}"
