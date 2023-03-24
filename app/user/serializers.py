"""
Serializers for the user API View.
"""

from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer as BaseTokenObtainPairSerializer,
    ValidationError,
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        model = get_user_model()
        fields = ["email", "name", "password"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
            }
        }

    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return a user with encrypted password."""

        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class TokenObtainPairSerializer(BaseTokenObtainPairSerializer):
    """Serializer for obtaining the token pair."""

    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )

            if not user:
                raise ValidationError(
                    "Unable to authenticate with provided credentials.",
                    code="authorization",
                )

        data = super().validate(attrs)
        return data
