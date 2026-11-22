from django.shortcuts import render

from apps.projects.models import Project


def status_check(request):
    code = request.GET.get("code", "").strip()
    project = None
    if code:
        pk = Project.pk_from_code(code)
        if pk is not None:
            project = Project.objects.prefetch_related("barangay_links__barangay").filter(pk=pk).first()
    return render(request, "statuscheck/status_check.html", {"code": code, "project": project, "searched": bool(code)})
