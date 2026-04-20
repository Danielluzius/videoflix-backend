import django_rq
from user_app.utils import send_activation_email, send_password_reset_email


@django_rq.job
def task_send_activation_email(user):
    send_activation_email(user)


@django_rq.job
def task_send_password_reset_email(user):
    send_password_reset_email(user)
