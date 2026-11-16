"""Small helper shared by the apps' tests."""
from django.utils.text import slugify

from .models import Barangay, Category, Project


def make_project(barangay="Lahug", category="Livelihood", **kw):
    b, _ = Barangay.objects.get_or_create(name=barangay)
    c, _ = Category.objects.get_or_create(name=category, defaults={"slug": slugify(category)})
    kw.setdefault("title", "Skills training")
    kw.setdefault("budget", 100000)
    kw.setdefault("fiscal_year", 2026)
    return Project.objects.create(barangay=b, category=c, **kw)
