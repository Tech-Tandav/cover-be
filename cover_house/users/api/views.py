from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from cover_house.users.models import User

from .serializers import CustomTokenObtainPairSerializer, UserSerializer


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class UserRegisterationView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserLoginTokenView(TokenObtainPairView):
    """
    POST username + password → { access, refresh, user }.
    Replace any prior DRF Token auth: clients now send `Authorization: Bearer <access>`.
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class UserLogoutView(CreateAPIView):
    """
    POST { "refresh": "<refresh_token>" } to blacklist the refresh token so it
    can no longer be used. Requires SIMPLE_JWT['BLACKLIST_AFTER_ROTATION'] and
    the token_blacklist app (both enabled in settings).
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer  # placeholder for schema; not used

    def create(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception as exc:  # noqa: BLE001
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )
        return Response(status=status.HTTP_205_RESET_CONTENT)
