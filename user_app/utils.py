from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings


def build_activation_link(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"{settings.FRONTEND_URL}/activate/{uid}/{token}"


def build_password_reset_link(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"{settings.FRONTEND_URL}/password_confirm/{uid}/{token}"


def send_activation_email(user):
    link = build_activation_link(user)
    context = {'link': link, 'email': user.email}
    html = render_to_string('emails/activation_email.html', context)
    text = f"Aktiviere deinen Account: {link}"
    msg = EmailMultiAlternatives(
        subject='Videoflix – Account aktivieren',
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html, 'text/html')
    msg.send()


def send_password_reset_email(user):
    link = build_password_reset_link(user)
    context = {'link': link, 'email': user.email}
    html = render_to_string('emails/password_reset_email.html', context)
    text = f"Passwort zurücksetzen: {link}"
    msg = EmailMultiAlternatives(
        subject='Videoflix – Passwort zurücksetzen',
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html, 'text/html')
    msg.send()
