"""Small helpers shared by the apps' tests."""
from .models import Barangay, BarangayProject, Project


def make_barangay(name="Lahug"):
    return Barangay.objects.get_or_create(barangay_name=name)[0]


def make_project(barangay="Lahug", sitio="Sitio Mahayag", **kw):
    kw.setdefault("project_name", "Skills training")
    kw.setdefault("amount", 100000)
    project = Project.objects.create(**kw)
    BarangayProject.objects.create(project=project, barangay=make_barangay(barangay), sitio=sitio)
    return project
