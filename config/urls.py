from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "CivicLens administration"
admin.site.site_title = "CivicLens"
admin.site.index_title = "Manage LDF projects, barangays and accounts"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("apps.accounts.urls")),      # login, logout, my projects
    path("projects/", include("apps.projects.urls")),      # search, detail, update status
    path("check/", include("apps.statuscheck.urls")),      # status checker
    path("manage/", include("apps.projectmanager.urls")),
    path("", include("apps.dashboard.urls")),              # home dashboard + stats API
    
]
