from django.db.models import Count, Q

from .models import STATUS_COLORS, Status


def status_summary(qs):
    """Count of projects per status, in pipeline order, with display colours."""
    counts = dict(qs.values_list("status").annotate(n=Count("id")))
    return [
        {"key": s.value, "label": s.label, "count": counts.get(s.value, 0), "color": STATUS_COLORS[s.value]}
        for s in Status
    ]


def filter_projects(qs, params):
    q = params.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(code__icontains=q)
            | Q(barangay__name__icontains=q) | Q(category__name__icontains=q)
        )
    if params.get("category"):
        qs = qs.filter(category__slug=params["category"])
    if params.get("status") in Status.values:
        qs = qs.filter(status=params["status"])
    if params.get("barangay", "").isdigit():
        qs = qs.filter(barangay_id=int(params["barangay"]))
    return qs
