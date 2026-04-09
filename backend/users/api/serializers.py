from rest_framework import serializers

from backend.users.models import LoyaltyAccount, LoyaltyTransaction, User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["username", "name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"},
        }


class LoyaltyTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoyaltyTransaction
        fields = [
            "id",
            "kind",
            "points",
            "balance_after",
            "reason",
            "order",
            "created_at",
        ]
        read_only_fields = fields


class LoyaltyAccountSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    recent_transactions = serializers.SerializerMethodField()

    class Meta:
        model = LoyaltyAccount
        fields = [
            "id",
            "username",
            "points",
            "lifetime_points",
            "tier",
            "joined_at",
            "updated_at",
            "recent_transactions",
        ]
        read_only_fields = fields

    def get_recent_transactions(self, obj: LoyaltyAccount):
        qs = obj.transactions.all()[:10]
        return LoyaltyTransactionSerializer(qs, many=True).data


class LoyaltyMovementSerializer(serializers.Serializer):
    """Input shape for the earn/redeem custom actions."""

    points = serializers.IntegerField(min_value=1)
    reason = serializers.CharField(max_length=200, required=False, allow_blank=True)
    order = serializers.PrimaryKeyRelatedField(
        queryset=None,  # set in __init__ to avoid circular import at module load
        required=False,
        allow_null=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from backend.orders.models import Order  # local import — avoids cycles

        self.fields["order"].queryset = Order.objects.all()
