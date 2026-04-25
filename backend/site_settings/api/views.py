from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.site_settings.models import SiteSettings

from .serializers import SiteSettingsSerializer


class SiteSettingsView(APIView):
    """GET/PATCH/PUT the singleton site settings."""

    permission_classes = [AllowAny]

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
