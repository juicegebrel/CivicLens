from django.db.models import Count, Q, Sum
from django.utils import timezone

from apps.projects.models import COMMITTED_STATUSES, STATUS_COLORS, BarangayProject, Project, Status
from apps.projects.services import status_summary


def build_stats():
    projects = Project.objects.all()
    totals = projects.aggregate(
        allocated=Sum("amount"),
        committed=Sum("amount", filter=Q(status__in=COMMITTED_STATUSES)),
        completed=Sum("amount", filter=Q(status=Status.COMPLETED)),
    )
    allocated = float(totals["allocated"] or 0)
    committed = float(totals["committed"] or 0)

    barangays = {}
    rows = (
        BarangayProject.objects.order_by()
        .values("barangay_id", "barangay__barangay_name", "project__status")
        .annotate(n=Count("pk"))
    )
    for r in rows:
        b = barangays.setdefault(
            r["barangay_id"],
            {"id": r["barangay_id"], "name": r["barangay__barangay_name"], "total": 0, "by_status": {}},
        )
        b["total"] += r["n"]
        b["by_status"][r["project__status"]] = r["n"]

    recent = [
        {
            "code": p.code,
            "title": p.project_name,
            "barangay": ", ".join(link.barangay.barangay_name for link in p.barangay_links.all()),
            "status": p.get_status_display(),
            "color": STATUS_COLORS[p.status],
            "when": p.project_date.strftime("%b %d, %Y"),
        }
        for p in projects.prefetch_related("barangay_links__barangay")[:6]
    ]
    return {
        "total": projects.count(),
        "total_allocated": allocated,
        "total_committed": committed,
        "total_completed": float(totals["completed"] or 0),
        "committed_percent": round(committed / allocated * 100) if allocated else 0,
        "barangays_covered": len(barangays),
        "statuses": status_summary(projects),
        "barangays": sorted(barangays.values(), key=lambda b: -b["total"])[:8],
        "recent": recent,
        "as_of": timezone.localtime().strftime("%b %d, %Y %I:%M %p"),
    }
