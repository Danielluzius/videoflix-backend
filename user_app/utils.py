"""Email helpers: build activation/reset links and send HTML emails with inline logo."""
import os
from email.mime.image import MIMEImage

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings

LOGO_PATH = os.path.join(settings.BASE_DIR, 'static', 'emails', 'logo.png')


def _attach_logo(msg):
    """Attach the Videoflix logo as an inline CID image to the given email message."""
    with open(LOGO_PATH, 'rb') as f:
        logo = MIMEImage(f.read())
    logo.add_header('Content-ID', '<videoflix_logo>')
    logo.add_header('Content-Disposition', 'inline', filename='logo.png')
    msg.attach(logo)


def build_activation_link(user):
    """Return the frontend activation URL containing uid and token for the given user."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"{settings.FRONTEND_URL}/pages/auth/activate.html?uid={uid}&token={token}"


def build_password_reset_link(user):
    """Return the frontend password-reset URL containing uid and token for the given user."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html?uid={uid}&token={token}"


def send_activation_email(user):
    """Build and send an HTML activation email with an inline logo to the given user."""
    link = build_activation_link(user)
    context = {'link': link, 'email': user.email}
    html = render_to_string('emails/activation_email.html', context)
    text = f"Aktiviere deinen Account: {link}"
    msg = EmailMultiAlternatives(
        subject='Confirm your email',
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html, 'text/html')
    _attach_logo(msg)
    msg.send()


def send_password_reset_email(user):
    """Build and send an HTML password-reset email with an inline logo to the given user."""
    link = build_password_reset_link(user)
    context = {'link': link, 'email': user.email}
    html = render_to_string('emails/password_reset_email.html', context)
    text = f"Passwort zurücksetzen: {link}"
    msg = EmailMultiAlternatives(
        subject='Reset your Password',
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    msg.attach_alternative(html, 'text/html')
    _attach_logo(msg)
    msg.send()
