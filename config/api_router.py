from django.conf import settings
from django.urls import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

# Public catalog (read-only)
from cover_house.cases.api.views import (
    CaseCategoryViewSet,
    CaseColorViewSet,
    CoverSkuViewSet,
)
from cover_house.phones.api.views import (
    BrandViewSet,
    PhoneModelViewSet,
    PhoneVariantViewSet,
    SeriesViewSet,
)

# Cart / orders (authenticated customer)
from cover_house.orders.api.views import (
    AddressViewSet,
    CartItemViewSet,
    CartView,
    CheckoutView,
    OrderViewSet,
)

# Admin write API
from cover_house.cases.api.admin_views import (
    CaseCategoryAdminViewSet,
    CaseColorAdminViewSet,
    CoverImageAdminViewSet,
    CoverSkuAdminViewSet,
)
from cover_house.orders.api.admin_views import OrderAdminViewSet
from cover_house.phones.api.admin_views import (
    BrandAdminViewSet,
    PhoneModelAdminViewSet,
    PhoneVariantAdminViewSet,
    SeriesAdminViewSet,
)

# Auth
from cover_house.users.api.views import (
    UserLoginTokenView,
    UserLogoutView,
    UserRegisterationView,
    UserViewSet,
)


def _router():
    return DefaultRouter() if settings.DEBUG else SimpleRouter()


# ─── Public + customer router ────────────────────────────────────────────────
router = _router()

router.register("users", UserViewSet)

# Phone taxonomy (public read)
router.register("brands", BrandViewSet, basename="brand")
router.register("series", SeriesViewSet, basename="series")
router.register("phone-models", PhoneModelViewSet, basename="phone-model")
router.register("phone-variants", PhoneVariantViewSet, basename="phone-variant")

# Covers (public read)
router.register("case-categories", CaseCategoryViewSet, basename="case-category")
router.register("case-colors", CaseColorViewSet, basename="case-color")
router.register("covers", CoverSkuViewSet, basename="cover")

# Cart / orders (authenticated)
router.register("addresses", AddressViewSet, basename="address")
router.register("cart/items", CartItemViewSet, basename="cart-item")
router.register("orders", OrderViewSet, basename="order")


# ─── Admin router (mounted under /api/admin/) ────────────────────────────────
admin_router = _router()
admin_router.register("brands", BrandAdminViewSet, basename="admin-brand")
admin_router.register("series", SeriesAdminViewSet, basename="admin-series")
admin_router.register("phone-models", PhoneModelAdminViewSet, basename="admin-phone-model")
admin_router.register("phone-variants", PhoneVariantAdminViewSet, basename="admin-phone-variant")
admin_router.register("case-categories", CaseCategoryAdminViewSet, basename="admin-case-category")
admin_router.register("case-colors", CaseColorAdminViewSet, basename="admin-case-color")
admin_router.register("covers", CoverSkuAdminViewSet, basename="admin-cover")
admin_router.register("cover-images", CoverImageAdminViewSet, basename="admin-cover-image")
admin_router.register("orders", OrderAdminViewSet, basename="admin-order")


app_name = "api"

urlpatterns = [
    # Auth
    path("register/", UserRegisterationView.as_view(), name="register"),
    path("login/", UserLoginTokenView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),

    # Cart & checkout
    path("cart/", CartView.as_view(), name="cart"),
    path("checkout/", CheckoutView.as_view(), name="checkout"),

    # Admin namespace
    path("admin/", include((admin_router.urls, "admin-api"), namespace="admin")),
]
urlpatterns += router.urls
