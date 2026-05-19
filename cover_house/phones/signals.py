"""
Keep PhoneVariant.full_name in sync with the Brand > Series > Model > Variant
chain whenever any link in the chain changes. We use .update() (not .save())
to write the denormalised value so the PhoneVariant post_save signal does not
recurse infinitely.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from cover_house.phones.models import Brand, PhoneModel, PhoneVariant, Series


def _refresh_variant(variant: PhoneVariant) -> None:
    expected = variant.compute_full_name()
    if variant.full_name != expected:
        PhoneVariant.objects.filter(pk=variant.pk).update(full_name=expected)


def _refresh_variants_qs(qs):
    for variant in qs.select_related("phone_model__series__brand"):
        _refresh_variant(variant)


@receiver(post_save, sender=PhoneVariant)
def variant_saved(sender, instance, **kwargs):
    _refresh_variant(instance)


@receiver(post_save, sender=PhoneModel)
def phone_model_saved(sender, instance, **kwargs):
    _refresh_variants_qs(instance.variants.all())


@receiver(post_save, sender=Series)
def series_saved(sender, instance, **kwargs):
    _refresh_variants_qs(
        PhoneVariant.objects.filter(phone_model__series=instance)
    )


@receiver(post_save, sender=Brand)
def brand_saved(sender, instance, **kwargs):
    _refresh_variants_qs(
        PhoneVariant.objects.filter(phone_model__series__brand=instance)
    )
