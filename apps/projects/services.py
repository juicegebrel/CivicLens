from django.db.models import Count, Q

from .models import STATUS_COLORS, Status


def status_summary(qs):
    """Count of projects per status, in pipeline order, with display colours."""
    counts = dict(qs.order_by().values_list("status").annotate(n=Count("pk")))
    return [
        {"key": s.value, "label": s.label, "count": counts.get(s.value, 0), "color": STATUS_COLORS[s.value]}
        for s in Status
    ]


def filter_projects(qs, params):
    q = params.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(project_name__icontains=q)
            | Q(barangays__barangay_name__icontains=q)
            | Q(barangay_links__sitio__icontains=q)
        )
    if params.get("status") in Status.values:
        qs = qs.filter(status=params["status"])
    if params.get("barangay", "").isdigit():
        qs = qs.filter(barangays__pk=int(params["barangay"]))
    return qs.distinct()
