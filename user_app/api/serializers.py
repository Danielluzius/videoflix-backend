from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """Validate registration input: email uniqueness and matching passwords."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Ensure passwords match and the email is not already in use."""
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError('Passwords do not match.')
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError('Email already registered.')
        return data


class LoginSerializer(serializers.Serializer):
    """Validate login input: email and password fields."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class PasswordResetSerializer(serializers.Serializer):
    """Validate password reset request input: email field."""

    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):
    """Validate new password input: new_password and confirm_password must match."""

    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Ensure new_password and confirm_password are identical."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError('Passwords do not match.')
        return data
