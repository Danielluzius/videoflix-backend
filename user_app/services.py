from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode

User = get_user_model()


def create_user(email, password):
    user = User.objects.create_user(email=email, password=password)
    return user


def activate_user(uidb64, token):
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
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def set_new_password(uidb64, token, password):
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
