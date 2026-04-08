from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.site_settings.models import SiteSettings

from .serializers import SiteSettingsSerializer


class SiteSettingsView(APIView):
    """GET (public) and PATCH/PUT (admin) the singleton site settings."""

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        instance = SiteSettings.load()
        return Response(SiteSettingsSerializer(instance).data)

    def patch(self, request):
        instance = SiteSettings.load()
        serializer = SiteSettingsSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def put(self, request):
        instance = SiteSettings.load()
        serializer = SiteSettingsSerializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
