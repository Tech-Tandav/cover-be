from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from cover_house.users.models import User


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["username", "name", "url"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"},
        }


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Returns access + refresh tokens plus a small user payload so the client
    can hydrate state in a single round-trip.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Custom claims embedded in the access token itself
        token["username"] = user.username
        token["is_staff"] = user.is_staff
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "username": self.user.username,
            "is_staff": self.user.is_staff,
        }
        return data
