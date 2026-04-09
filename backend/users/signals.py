from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.users.models import LoyaltyAccount


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_loyalty_account(sender, instance, created, **kwargs):
    """Every newly created user gets an empty loyalty wallet so the rest of
    the codebase can assume `user.loyalty` always exists."""
    if created:
        LoyaltyAccount.objects.get_or_create(user=instance)
