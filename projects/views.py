from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from accounts.decorators import staff_required

from .forms import ProjectStatusForm
from .models import Barangay, Category, Project, Status
from .services import filter_projects


def project_list(request):
    qs = filter_projects(Project.objects.select_related("barangay", "category"), request.GET)
    page_obj = Paginator(qs, 10).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "projects/project_list.html", {
        "page_obj": page_obj,
        "result_count": page_obj.paginator.count,
        "categories": Category.objects.all(),
        "barangays": Barangay.objects.all(),
        "statuses": Status.choices,
        "f": request.GET,
        "querystring": params.urlencode(),
    })


def project_detail(request, code):
    project = get_object_or_404(Project.objects.select_related("barangay", "category"), code__iexact=code)
    return render(request, "projects/project_detail.html", {
        "project": project,
        "updates": project.updates.select_related("updated_by"),
        "can_update": request.user.is_staff,
    })


@staff_required
def update_status(request, code):
    project = get_object_or_404(Project, code__iexact=code)
    form = ProjectStatusForm(request.POST or None, project=project, initial={
        "status": project.status,
        "progress_percent": project.progress_percent,
        "amount_utilized": project.amount_utilized,
    })
    if request.method == "POST" and form.is_valid():
        d = form.cleaned_data
        project.apply_update(
            d["status"], d["progress_percent"], d["remarks"], request.user, d["amount_utilized"]
        )
        messages.success(request, f"{project.code} is now marked “{project.get_status_display()}”.")
        return redirect(project)
    return render(request, "projects/update_status.html", {"project": project, "form": form})
