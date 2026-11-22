from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import BarangayOfficial, CityOfficial


class CityOfficialInline(admin.StackedInline):
    model = CityOfficial
    extra = 0


class BarangayOfficialInline(admin.StackedInline):
    model = BarangayOfficial
    extra = 0


User = get_user_model()
admin.site.unregister(User)


@admin.register(User)
class CivicLensUserAdmin(UserAdmin):
    inlines = [CityOfficialInline, BarangayOfficialInline]


@admin.register(BarangayOfficial)
class BarangayOfficialAdmin(admin.ModelAdmin):
    list_display = ("user", "barangay")
    list_filter = ("barangay",)
    search_fields = ("user__username", "user__first_name", "user__last_name")


admin.site.register(CityOfficial)
