from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from backend.catalog.api.views import (
    BrandViewSet,
    CategoryViewSet,
    PhoneModelViewSet,
    ProductViewSet,
    VariantViewSet,
)
from backend.expenses.api.views import ExpenseViewSet
from backend.orders.api.views import OrderViewSet
from backend.site_settings.api.views import SiteSettingsView
from backend.users.api.views import (
    UserLoginTokenView,
    UserRegisterationView,
    UserViewSet,
)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("catalog/categories", CategoryViewSet, basename="category")
router.register("catalog/brands", BrandViewSet, basename="brand")
router.register("catalog/phone-models", PhoneModelViewSet, basename="phone-model")
router.register("catalog/variants", VariantViewSet, basename="variant")
router.register("catalog/products", ProductViewSet, basename="product")
router.register("orders/orders", OrderViewSet, basename="order")
router.register("expenses/expenses", ExpenseViewSet, basename="expense")


app_name = "api"

urlpatterns = [
    path("register/", UserRegisterationView.as_view(), name="register"),
    path("login/", UserLoginTokenView.as_view(), name="login"),
    path("site/settings/", SiteSettingsView.as_view(), name="site-settings"),
]
urlpatterns += router.urls
