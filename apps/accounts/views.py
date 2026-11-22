from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.projects.models import Project
from apps.projects.services import status_summary

from .forms import RegisterForm
from .utils import is_city_official, user_barangay


def register(request):
    if request.user.is_authenticated:
        return redirect("my_projects")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome! You are registered as an official of Barangay {form.barangay}.")
        return redirect("my_projects")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def my_projects(request):
    barangay = user_barangay(request.user)
    if barangay:
        qs = Project.objects.filter(barangays=barangay)
    elif is_city_official(request.user):
        qs = Project.objects.all()
    else:
        qs = Project.objects.none()
    qs = qs.prefetch_related("barangay_links__barangay")
    return render(request, "accounts/my_projects.html", {
        "barangay": barangay,
        "is_city_official": is_city_official(request.user),
        "projects": qs,
        "statuses": status_summary(qs),
    })
