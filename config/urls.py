from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "CivicLens administration"
admin.site.site_title = "CivicLens"
admin.site.index_title = "Manage LDF projects, barangays and accounts"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),      # login, logout, my projects
    path("projects/", include("projects.urls")),      # search, detail, update status
    path("check/", include("statuscheck.urls")),      # status checker
    path("", include("dashboard.urls")),              # home dashboard + stats API
]
