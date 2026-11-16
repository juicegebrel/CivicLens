from django.db.models import Avg, Count, Sum
from django.utils import timezone

from projects.models import STATUS_COLORS, Project, StatusUpdate
from projects.services import status_summary


def build_stats():
    projects = Project.objects.all()
    totals = projects.aggregate(budget=Sum("budget"), progress=Avg("progress_percent"))
    completed_budget = projects.filter(status=Status.COMPLETED).aggregate(b=Sum("budget"))["b"] or 0

    categories = {}
    rows = projects.values("category__name", "category__slug", "status").annotate(n=Count("id"))
    for r in rows:
        c = categories.setdefault(
            r["category__slug"], {"name": r["category__name"], "slug": r["category__slug"], "total": 0, "by_status": {}}
        )
        c["total"] += r["n"]
        c["by_status"][r["status"]] = r["n"]

    recent = [
        {
            "code": u.project.code,
            "title": u.project.title,
            "barangay": u.project.barangay.name,
            "status": u.get_status_display(),
            "color": STATUS_COLORS[u.status],
            "when": timezone.localtime(u.created_at).strftime("%b %d, %Y"),
        }
        for u in StatusUpdate.objects.select_related("project__barangay")[:6]
    ]
    return {
        "total": projects.count(),
        "avg_progress": round(totals["progress"] or 0),
        "total_budget": float(totals["budget"] or 0),
        "completed_budget": float(completed_budget),
        "statuses": status_summary(projects),
        "categories": sorted(categories.values(), key=lambda c: -c["total"]),
        "recent": recent,
        "as_of": timezone.localtime().strftime("%b %d, %Y %I:%M %p"),
    }
