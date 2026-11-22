from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.decorators import city_official_required
from apps.accounts.utils import is_city_official

from .forms import ProjectStatusForm
from .models import Barangay, Project, Status
from .services import filter_projects

WITH_BARANGAYS = "barangay_links__barangay"


def project_list(request):
    qs = filter_projects(Project.objects.prefetch_related(WITH_BARANGAYS), request.GET)
    page_obj = Paginator(qs, 10).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)
    return render(request, "projects/project_list.html", {
        "page_obj": page_obj,
        "result_count": page_obj.paginator.count,
        "barangays": Barangay.objects.all(),
        "statuses": Status.choices,
        "f": request.GET,
        "querystring": params.urlencode(),
    })


def project_detail(request, code):
    project = get_object_or_404(Project.objects.prefetch_related(WITH_BARANGAYS), pk=Project.pk_from_code(code))
    return render(request, "projects/project_detail.html", {
        "project": project,
        "can_update": is_city_official(request.user),
    })


@city_official_required
def update_status(request, code):
    project = get_object_or_404(Project, pk=Project.pk_from_code(code))
    form = ProjectStatusForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{project.code} is now marked “{project.get_status_display()}”.")
        return redirect(project)
    return render(request, "projects/update_status.html", {"project": project, "form": form})
