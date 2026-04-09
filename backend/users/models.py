from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class InsufficientPointsError(Exception):
    """Raised when a redeem is attempted for more points than the account holds."""


class User(AbstractUser):
    """
    Default custom user model for backend.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})


class LoyaltyAccount(models.Model):
    """Per-customer loyalty wallet. Tracks current point balance, lifetime
    points earned, and the customer's current tier."""

    class Tier(models.TextChoices):
        BRONZE = "bronze", _("Bronze")
        SILVER = "silver", _("Silver")
        GOLD = "gold", _("Gold")
        PLATINUM = "platinum", _("Platinum")

    # Lifetime-points thresholds at which a customer is promoted to each tier.
    # Ordered low → high so the loop in `_recompute_tier` picks the highest match.
    TIER_THRESHOLDS = (
        (Tier.BRONZE, 0),
        (Tier.SILVER, 500),
        (Tier.GOLD, 2_000),
        (Tier.PLATINUM, 10_000),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="loyalty",
    )
    points = models.PositiveIntegerField(
        default=0,
        help_text="Current redeemable point balance.",
    )
    lifetime_points = models.PositiveIntegerField(
        default=0,
        help_text="Total points ever earned. Drives tier progression.",
    )
    tier = models.CharField(
        max_length=20,
        choices=Tier.choices,
        default=Tier.BRONZE,
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Loyalty account"
        verbose_name_plural = "Loyalty accounts"

    def __str__(self) -> str:
        return f"{self.user} — {self.points} pts ({self.tier})"

    def _recompute_tier(self) -> None:
        new_tier = self.Tier.BRONZE
        for tier, threshold in self.TIER_THRESHOLDS:
            if self.lifetime_points >= threshold:
                new_tier = tier
        self.tier = new_tier

    @transaction.atomic
    def earn(
        self,
        amount: int,
        *,
        reason: str = "",
        order=None,
    ) -> "LoyaltyTransaction":
        """Credit points to this account and write a ledger entry. Bumps
        lifetime_points and re-evaluates tier."""
        if amount <= 0:
            msg = "Earn amount must be positive."
            raise ValueError(msg)

        # Lock this row so concurrent earn/redeem can't race the balance.
        locked = LoyaltyAccount.objects.select_for_update().get(pk=self.pk)
        locked.points += amount
        locked.lifetime_points += amount
        locked._recompute_tier()
        locked.save(update_fields=["points", "lifetime_points", "tier", "updated_at"])

        # Refresh in-memory copy so callers see the new state.
        self.points = locked.points
        self.lifetime_points = locked.lifetime_points
        self.tier = locked.tier

        return LoyaltyTransaction.objects.create(
            account=self,
            kind=LoyaltyTransaction.Kind.EARN,
            points=amount,
            balance_after=locked.points,
            reason=reason,
            order=order,
        )

    @transaction.atomic
    def redeem(
        self,
        amount: int,
        *,
        reason: str = "",
        order=None,
    ) -> "LoyaltyTransaction":
        """Debit points from this account and write a ledger entry. Does NOT
        touch lifetime_points (so tier stays sticky after redemption)."""
        if amount <= 0:
            msg = "Redeem amount must be positive."
            raise ValueError(msg)

        locked = LoyaltyAccount.objects.select_for_update().get(pk=self.pk)
        if locked.points < amount:
            raise InsufficientPointsError(
                f"Cannot redeem {amount} pts — balance is {locked.points}.",
            )
        locked.points -= amount
        locked.save(update_fields=["points", "updated_at"])

        self.points = locked.points

        return LoyaltyTransaction.objects.create(
            account=self,
            kind=LoyaltyTransaction.Kind.REDEEM,
            points=amount,
            balance_after=locked.points,
            reason=reason,
            order=order,
        )


class LoyaltyTransaction(models.Model):
    """Append-only ledger of every points movement on a loyalty account.
    The current `LoyaltyAccount.points` value should always equal the running
    sum of these entries (earn = +points, redeem = −points)."""

    class Kind(models.TextChoices):
        EARN = "earn", _("Earn")
        REDEEM = "redeem", _("Redeem")
        ADJUST = "adjust", _("Manual adjustment")

    account = models.ForeignKey(
        LoyaltyAccount,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    kind = models.CharField(max_length=10, choices=Kind.choices)
    points = models.PositiveIntegerField(
        help_text="Magnitude of the movement; sign is implied by `kind`.",
    )
    balance_after = models.PositiveIntegerField(
        help_text="Account balance immediately after this transaction was applied.",
    )
    reason = models.CharField(max_length=200, blank=True, default="")
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="loyalty_transactions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["account", "-created_at"]),
        ]

    def __str__(self) -> str:
        sign = "+" if self.kind == self.Kind.EARN else "-"
        return f"{self.account.user} {sign}{self.points} ({self.kind})"
