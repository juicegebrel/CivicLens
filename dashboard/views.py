from django.http import JsonResponse
from django.shortcuts import render

from .services import build_stats


def dashboard(request):
    return render(request, "dashboard/dashboard.html", {"stats": build_stats()})


def stats_api(request):
    return JsonResponse(build_stats())
