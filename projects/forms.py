from django import forms

from .models import Status


class ProjectStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Status.choices)
    progress_percent = forms.IntegerField(min_value=0, max_value=100, label="Progress (%)")
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}), required=False,
        help_text="Shown to the public in the project's update history.",
    )
