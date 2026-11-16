from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from projects.models import Project
from projects.services import status_summary

from .forms import RegisterForm
from .utils import user_barangay


def register(request):
    if request.user.is_authenticated:
        return redirect("my_projects")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome to CivicLens. Your account is ready.")
        return redirect("my_projects")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def my_projects(request):
    barangay = user_barangay(request.user)
    if barangay:
        qs = Project.objects.filter(barangay=barangay)
    elif request.user.is_staff:
        qs = Project.objects.all()
    else:
        qs = Project.objects.none()
    qs = qs.select_related("barangay", "category")
    return render(request, "accounts/my_projects.html", {
        "barangay": barangay,
        "projects": qs,
        "statuses": status_summary(qs),
    })