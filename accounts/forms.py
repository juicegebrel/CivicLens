from django import forms
from django.contrib.auth.forms import UserCreationForm

from projects.models import Barangay

from .models import Profile


class RegisterForm(UserCreationForm):
    barangay = forms.ModelChoiceField(
        queryset=Barangay.objects.all(),
        empty_label="Select your barangay",
        help_text="Your barangay decides which projects appear under My projects.",
    )

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Profile.objects.update_or_create(user=user, defaults={"barangay": self.cleaned_data["barangay"]})
        return user