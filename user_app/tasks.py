import django_rq
from user_app.utils import send_activation_email, send_password_reset_email


@django_rq.job('emails')
def task_send_activation_email(user):
    """Background task: send account activation email to the given user."""
    send_activation_email(user)


@django_rq.job('emails')
def task_send_password_reset_email(user):
    """Background task: send password reset email to the given user."""
    send_password_reset_email(user)
