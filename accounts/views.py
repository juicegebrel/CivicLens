from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from projects.models import Project
from projects.services import status_summary

from .utils import user_barangay


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
