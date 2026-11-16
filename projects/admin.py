from django.contrib import admin
from .models import Barangay, Category, Project, StatusUpdate


class StatusUpdateInline(admin.TabularInline):
    model = StatusUpdate
    extra = 0
    readonly_fields = ("status", "progress_percent", "remarks", "updated_by", "created_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "barangay", "category", "status", "progress_percent", "budget", "amount_utilized", "fiscal_year")
    list_filter = ("status", "category", "barangay", "fiscal_year")
    search_fields = ("code", "title", "description", "barangay__name")
    readonly_fields = ("code", "created_at", "updated_at")
    inlines = [StatusUpdateInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Keep the public update history in step with edits made here.
        if not change or {"status", "progress_percent"} & set(form.changed_data):
            StatusUpdate.objects.create(
                project=obj, status=obj.status, progress_percent=obj.progress_percent,
                remarks="Project encoded." if not change else "Updated by CPDO.", updated_by=request.user,
            )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Barangay)
