from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from apps.projects.models import Barangay

from .models import BarangayOfficial

User = get_user_model()


class RegisterForm(UserCreationForm):
    """Registers a barangay official. The barangay is found from its secret code."""

    barangay_code = forms.CharField(
        max_length=50,
        help_text="Ask your barangay or the CPDO for your barangay's registration code.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("first_name", "last_name", "email"):
            self.fields[name].required = True
        self.barangay = None

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_barangay_code(self):
        code = self.cleaned_data["barangay_code"].strip().upper()
        try:
            self.barangay = Barangay.objects.get(barangay_code=code)
        except Barangay.DoesNotExist:
            raise forms.ValidationError("That code doesn't match any barangay. Check it and try again.")
        return code

    def save(self, commit=True):
        with transaction.atomic():
            user = super().save(commit=True)
            BarangayOfficial.objects.create(user=user, barangay=self.barangay)
        return user
