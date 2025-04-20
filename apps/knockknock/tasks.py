from celery import shared_task
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
# from apps.community.models import Partnership
from .settings import settings
from .models import User
from .utils import send_activation_link, send_password_reset_link, send_request_received, send_request_responded, send_invitation_email
from .tokens import RegisterTokenGenerator

@shared_task
def send_user_activation_email(user_id):
    '''
    Sends an email containing the activation token to the given user
    in order to verify Email address and activate user's account.
    '''
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return
    token_generator = RegisterTokenGenerator()
    token = token_generator.make_token(user=user)
    activation_link = settings.KK_ACCOUNT_ACTIVATION_URL+f"?u={user.id}&t={token}"
    send_activation_link(recipient=user, link=activation_link)

@shared_task
def send_password_reset_email(email):
    '''
    Sends and email containing the link to password reset page.
    '''
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return False
    token_generator = PasswordResetTokenGenerator()
    token = token_generator.make_token(user=user)
    passsword_reset_link = settings.KK_PASSWORD_RESET_URL+f"?user_id={user.id}&token={token}"
    send_password_reset_link(recipient=user, link=passsword_reset_link)
    return True

@shared_task
def send_invitation(email):
    send_invitation_email(email)
    return True