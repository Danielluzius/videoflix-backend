"""Service layer for user-related database operations."""
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

User = get_user_model()


def create_user(email, password):
    """Create an inactive user account with the given email and password."""
    user = User.objects.create_user(email=email, password=password)
    return user


def activate_user(uidb64, token):
    """Decode the uid, validate the token, and activate the user account.

    Returns the activated User on success, or None if the token is invalid.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        return None
    if not default_token_generator.check_token(user, token):
        return None
    user.is_active = True
    user.save()
    return user


def get_user_for_password_reset(email):
    """Return the user with the given email, or None if no account exists."""
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def set_new_password(uidb64, token, password):
    """Validate the reset token and set a new password for the user.

    Returns the updated User on success, or None if the token is invalid.
    """
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError):
        return None
    if not default_token_generator.check_token(user, token):
        return None
    user.set_password(password)
    user.save()
    return user
