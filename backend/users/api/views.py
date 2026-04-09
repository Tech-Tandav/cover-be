from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin
from rest_framework.mixins import RetrieveModelMixin
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.generics import CreateAPIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from backend.users.models import (
    InsufficientPointsError,
    LoyaltyAccount,
    User,
)

from .serializers import (
    LoyaltyAccountSerializer,
    LoyaltyMovementSerializer,
    LoyaltyTransactionSerializer,
    UserSerializer,
)


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


class LoyaltyAccountViewSet(RetrieveModelMixin, ListModelMixin, GenericViewSet):
    """Loyalty wallet endpoints.

    - Customers see only their own account via the `me` action.
    - Staff can list all accounts and trigger `earn` / `redeem` / `adjust`
      from this endpoint (e.g. from the dashboard or as part of order
      fulfillment / refund flows).
    """

    serializer_class = LoyaltyAccountSerializer
    queryset = LoyaltyAccount.objects.select_related("user").all()

    def get_permissions(self):
        if self.action in ("me", "my_transactions", "redeem"):
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        if self.action in ("list", "retrieve") and not self.request.user.is_staff:
            return self.queryset.filter(user=self.request.user)
        return self.queryset

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Current user's loyalty wallet. Auto-creates one if missing — this
        is a safety net for users who existed before the signal was added."""
        account, _ = LoyaltyAccount.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(account)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="me/transactions")
    def my_transactions(self, request):
        account, _ = LoyaltyAccount.objects.get_or_create(user=request.user)
        qs = account.transactions.all()
        page = self.paginate_queryset(qs)
        ser = LoyaltyTransactionSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(ser.data)
        return Response(ser.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser])
    def earn(self, request, pk=None):
        """Staff-only: credit points to a customer's account."""
        account = self.get_object()
        ser = LoyaltyMovementSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        tx = account.earn(
            amount=ser.validated_data["points"],
            reason=ser.validated_data.get("reason", ""),
            order=ser.validated_data.get("order"),
        )
        return Response(
            LoyaltyTransactionSerializer(tx).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def redeem(self, request):
        """Customer-facing: redeem points from the caller's own account.
        Lives at /api/users/loyalty/redeem/ rather than /<pk>/redeem/ so
        customers don't need to know their own account id."""
        account, _ = LoyaltyAccount.objects.get_or_create(user=request.user)
        ser = LoyaltyMovementSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            tx = account.redeem(
                amount=ser.validated_data["points"],
                reason=ser.validated_data.get("reason", ""),
                order=ser.validated_data.get("order"),
            )
        except InsufficientPointsError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            LoyaltyTransactionSerializer(tx).data,
            status=status.HTTP_201_CREATED,
        )


class UserRegisterationView(CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
        
        
class CoverTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Embeds custom claims into the access token AND returns a flat user
    payload alongside the tokens, so the frontend (NextAuth) can populate
    its session in a single round trip."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        token["is_staff"] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data["user"] = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "is_staff": user.is_staff,
        }
        # Back-compat alias: existing frontend reads `response.data.token`.
        # Drop this once the frontend has migrated to `access`/`refresh`.
        data["token"] = data["access"]
        return data


class UserLoginTokenView(TokenObtainPairView):
    """POST /api/login/ — returns `{ access, refresh, token, user }`.
    `token` mirrors `access` for back-compat with the existing axios client."""

    permission_classes = [AllowAny]
    serializer_class = CoverTokenObtainPairSerializer