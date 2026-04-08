from django.contrib import admin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("store_name", "phone", "email", "updated_at")

    def has_add_permission(self, request):
        # Singleton — only one row allowed.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
