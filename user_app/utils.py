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
    return f"{settings.FRONTEND_URL}/auth/activate?uid={uid}&token={token}"


def build_password_reset_link(user):
    """Return the frontend password-reset URL containing uid and token for the given user."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return f"{settings.FRONTEND_URL}/auth/confirm-password?uid={uid}&token={token}"


def _send_email(subject: str, text: str, html: str, recipient: str) -> None:
    """Send an HTML email with an inline Videoflix logo to a single recipient."""
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    msg.attach_alternative(html, 'text/html')
    _attach_logo(msg)
    msg.send()


def send_activation_email(user) -> None:
    """Build and send an HTML activation email with an inline logo to the given user."""
    link = build_activation_link(user)
    html = render_to_string('emails/activation_email.html', {'link': link, 'email': user.email})
    _send_email('Confirm your email', f"Activate your account: {link}", html, user.email)


def send_password_reset_email(user) -> None:
    """Build and send an HTML password-reset email with an inline logo to the given user."""
    link = build_password_reset_link(user)
    html = render_to_string('emails/password_reset_email.html', {'link': link, 'email': user.email})
    _send_email('Reset your Password', f"Reset your password: {link}", html, user.email)
