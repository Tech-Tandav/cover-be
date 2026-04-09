from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import LoyaltyAccount, LoyaltyTransaction, User

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]


class LoyaltyTransactionInline(admin.TabularInline):
    model = LoyaltyTransaction
    extra = 0
    can_delete = False
    readonly_fields = ["kind", "points", "balance_after", "reason", "order", "created_at"]
    ordering = ["-created_at"]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ["user", "tier", "points", "lifetime_points", "updated_at"]
    list_filter = ["tier"]
    search_fields = ["user__username", "user__email", "user__name"]
    readonly_fields = ["lifetime_points", "tier", "joined_at", "updated_at"]
    inlines = [LoyaltyTransactionInline]


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ["account", "kind", "points", "balance_after", "created_at"]
    list_filter = ["kind", "created_at"]
    search_fields = ["account__user__username", "reason"]
    readonly_fields = ["account", "kind", "points", "balance_after", "reason", "order", "created_at"]
    date_hierarchy = "created_at"
