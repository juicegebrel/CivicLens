from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Subquery
from django.shortcuts import redirect, render

from apps.projects.models import BarangayProject, Project
from apps.projects.services import status_summary

from .forms import RegisterForm
from .models import BarangayOfficial
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

def projects_of_official(user):
    """
    Projects of the barangay that `user` is an official of, found with nested subqueries.

    innermost: the barangay linked to this user in BarangayOfficial
    middle:    the projects linked to that barangay in BarangayProject
    outer:     the Project rows whose id is in that list
    """
    barangay_ids = BarangayOfficial.objects.filter(user=user).values("barangay_id")
    project_ids = BarangayProject.objects.filter(
        barangay_id__in=Subquery(barangay_ids)
    ).values("project_id")
    return Project.objects.filter(pk__in=Subquery(project_ids))

@login_required
def my_projects(request):
    barangay = user_barangay(request.user)
    if barangay:
        qs = projects_of_official(request.user)
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
        "can_edit": barangay is not None,
    })
