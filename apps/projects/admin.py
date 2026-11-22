from django.contrib import admin

from .models import Barangay, BarangayProject, Project


class BarangayProjectInline(admin.TabularInline):
    model = BarangayProject
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("project_id", "project_name", "status", "amount", "project_date")
    list_filter = ("status", "project_date")
    search_fields = ("project_name", "barangays__barangay_name")
    inlines = [BarangayProjectInline]


@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    list_display = ("barangay_name", "barangay_code")
    search_fields = ("barangay_name",)
    actions = ["regenerate_codes"]

    def get_fields(self, request, obj=None):
        # The code is generated automatically; show it once the barangay exists.
        return ("barangay_name", "barangay_code") if obj else ("barangay_name",)

    def get_readonly_fields(self, request, obj=None):
        return ("barangay_code",) if obj else ()

    @admin.action(description="Generate a new registration code")
    def regenerate_codes(self, request, queryset):
        for barangay in queryset:
            barangay.regenerate_code()
        self.message_user(request, f"New registration code generated for {queryset.count()} barangay(s).")
