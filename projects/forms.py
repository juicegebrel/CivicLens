from django import forms

from .models import Status


class ProjectStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Status.choices)
    progress_percent = forms.IntegerField(min_value=0, max_value=100, label="Progress (%)")
    amount_utilized = forms.DecimalField(
        min_value=0, max_digits=14, decimal_places=2, label="Amount utilized (₱)",
        help_text="Total money drawn from the approved budget so far.",
    )
    remarks = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3}), required=False,
        help_text="Shown to the public in the project's update history.",
    )

    def __init__(self, *args, project=None, **kwargs):
        self.project = project
        super().__init__(*args, **kwargs)

    def clean_amount_utilized(self):
        amount = self.cleaned_data["amount_utilized"]
        if self.project and amount > self.project.budget:
            raise forms.ValidationError(f"Cannot exceed the approved budget of ₱{self.project.budget:,.2f}.")
        return amount