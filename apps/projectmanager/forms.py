from django import forms
from django.db import transaction

from apps.projects.models import BarangayProject, Project


class ProjectForm(forms.ModelForm):
    """Add or edit a project for one barangay. Status is set by the CPDO, not here."""

    sitio = forms.CharField(
        max_length=50, required=False,
        help_text="Purok or sitio where the project is carried out (optional).",
    )

    class Meta:
        model = Project
        fields = ["project_name", "amount", "project_date"]
        labels = {
            "project_name": "Project name",
            "amount": "Allocated amount (₱)",
            "project_date": "Project date",
        }
        widgets = {"project_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def __init__(self, *args, barangay, **kwargs):
        self.barangay = barangay
        super().__init__(*args, **kwargs)
        self.fields["amount"].widget.attrs.update({"min": "0.01", "step": "0.01"})
        if self.instance.pk:
            link = self.instance.barangay_links.filter(barangay=barangay).first()
            if link:
                self.fields["sitio"].initial = link.sitio

    def clean_project_name(self):
        name = self.cleaned_data["project_name"].strip()
        duplicate = Project.objects.filter(project_name__iexact=name, barangays=self.barangay)
        if self.instance.pk:
            duplicate = duplicate.exclude(pk=self.instance.pk)
        if duplicate.exists():
            raise forms.ValidationError("Your barangay already has a project with this name.")
        return name

    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def save(self, commit=True):
        with transaction.atomic():
            project = super().save()
            BarangayProject.objects.update_or_create(
                project=project, barangay=self.barangay,
                defaults={"sitio": self.cleaned_data["sitio"].strip()},
            )
        return project
