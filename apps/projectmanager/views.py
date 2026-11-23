from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import barangay_official_required
from apps.projects.models import Project

from .forms import ProjectForm


@barangay_official_required
def project_create(request):
    form = ProjectForm(request.POST or None, barangay=request.barangay)
    if request.method == "POST" and form.is_valid():
        project = form.save()
        messages.success(request, f"Project added. Its reference code is {project.code}.")
        return redirect(project)
    return render(request, "projectmanager/project_form.html", {
        "form": form, "project": None, "barangay": request.barangay,
    })


@barangay_official_required
def project_edit(request, code):
    # Only projects linked to the official's own barangay can be edited.
    project = get_object_or_404(
        Project, pk=Project.pk_from_code(code), barangay_links__barangay=request.barangay
    )
    form = ProjectForm(request.POST or None, instance=project, barangay=request.barangay)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{project.code} was updated.")
        return redirect(project)
    return render(request, "projectmanager/project_form.html", {
        "form": form, "project": project, "barangay": request.barangay,
    })
