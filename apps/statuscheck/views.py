from django.shortcuts import render

from apps.projects.models import Project


def status_check(request):
    code = request.GET.get("code", "").strip()
    project = None
    if code:
        project = Project.objects.select_related("barangay", "category").filter(code__iexact=code).first()
    return render(request, "statuscheck/status_check.html", {"code": code, "project": project, "searched": bool(code)})
