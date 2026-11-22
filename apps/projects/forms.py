from django import forms

from .models import Project


class ProjectStatusForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["status"]
