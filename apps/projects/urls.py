from django.urls import path

from . import views

urlpatterns = [
    path("", views.project_list, name="project_list"),
    path("<str:code>/", views.project_detail, name="project_detail"),
    path("<str:code>/update/", views.update_status, name="update_status"),
]
