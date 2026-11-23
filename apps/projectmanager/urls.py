from django.urls import path

from . import views

urlpatterns = [
    path("new/", views.project_create, name="project_create"),
    path("<str:code>/edit/", views.project_edit, name="project_edit"),
]
