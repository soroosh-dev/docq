import random
import string
import jwt
import requests
# from web3.auto import w3
# from web3 import Web3
# from eth_keys.exceptions import BadSignature
# from eth_account.messages import encode_defunct
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .settings import settings
from .models import User

GOOGLE_ID_TOKEN_INFO_URL = 'https://www.googleapis.com/oauth2/v3/tokeninfo'
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = 'https://oauth2.googleapis.com/token'
GOOGLE_USER_INFO_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
FACEBOOK_ACCESS_TOKEN_OBTAIN_URL = 'https://graph.facebook.com/v19.0/oauth/access_token'
FACEBOOK_USER_INFO_URL = 'https://graph.facebook.com/v19.0/me'
APPLE_ACCESS_TOKEN_URL = 'https://appleid.apple.com/auth/token'

def send_password_reset_link(recipient, link):
    '''
    Sends password reset link via email to recipient.
    '''
    template_src = "auth/password_reset_email.html"
    context = {'password_reset_link': link}
    html_content = render_to_string(template_src, context)
    subject = 'Password reset'
    message = 'message' #TODO

    email_from = settings.EMAIL_HOST_USER
    recipient.email_user(subject, message, email_from, html_message=html_content)

def send_activation_link(recipient, link):
    '''
    Sends activation link via email to recipient.
    '''
    template_src = "auth/activation_email.html"
    context = {'activation_link': link}
    html_content = render_to_string(template_src, context)
    subject = 'Welcome'
    message = 'message' #TODO

    email_from = settings.EMAIL_HOST_USER
    recipient.email_user(subject, message, email_from, html_message=html_content)

def send_request_received(recipient, sender, receiver):
    template_src = 'auth/request_received.html'
    context = {'sender': sender, 'receiver': receiver}
    html_content = render_to_string(template_src, context)
    subject = "New partnership request"
    message = 'message'

    email_from = settings.EMAIL_HOST_USER
    recipient.email_user(subject, message, email_from, html_message=html_content)

def send_request_responded(recipient, receiver, accepted):
    template_src = 'auth/request_responded.html'
    context = {
        'receiver': receiver,
        'response': 'Accepted' if accepted else 'Rejected'
        }
    html_content = render_to_string(template_src, context)
    subject = "User has responded to partnership request"
    message = 'message'
    print(accepted)
    email_from = settings.EMAIL_HOST_USER
    recipient.email_user(subject, message, email_from, html_message=html_content)

def send_invitation_email(recipient):
    template_src = 'auth/invitation.html'
    html_content = render_to_string(template_src)
    subject = "Invitation"
    message = 'message'
    email_from = settings.EMAIL_HOST_USER
    send_mail(subject, message, email_from, html_message=html_content, recipient_list=[recipient])

def get_google_access_token(code):
    '''
    Uses returned code from google to obtain google's access token.
    '''
    data = {
        'code': code,
        'client_id': settings.KK_GOOGLE_CLIENT_ID,
        'client_secret': settings.KK_GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.KK_GOOGLE_LOGIN_CONFIRM_URL,
        'grant_type': 'authorization_code'
    }

    response = requests.post(GOOGLE_ACCESS_TOKEN_OBTAIN_URL, data=data)

    if not response.ok:
        return None
    access_token = response.json()['access_token']
    return access_token

def get_google_user_info(access_token):
    '''
    Uses access_token obtained from google to retrieve user's
    information.
    '''
    # TODO remove following 2 lines
    if access_token == 'kk':
        return {"email": "ghaffari.soroosh@gmail.com", "given_name": "srsh"}
    response = requests.get(
        GOOGLE_USER_INFO_URL,
        params={'access_token': access_token}
    )
    if not response.ok:
        return None
    return response.json()

def get_facebook_access_token(token):
    response = requests.get(
        FACEBOOK_ACCESS_TOKEN_OBTAIN_URL,
        params={'client_id': settings.KK_FACEBOOK_CLIENT_ID, 'redirect_uri': settings.KK_FACEBOOK_REDIRECT_URL, 'client_secret': settings.KK_FACEBOOK_CLIENT_SECRET, 'code': token}
    )
    if not response.ok:
        return None
    return response.json()['access_token']

def get_facebook_user_data(access_token):
    response = requests.get(
        FACEBOOK_USER_INFO_URL,
        params={'fields': 'id,email,first_name,last_name', 'access_token': access_token}
    )
    if not response.ok:
        return None
    return response.json()

def create_apple_client_secret():
    headers = {
        'kid': settings.KK_APPLE_KEY_ID
    }
    payload = {
        'iss': settings.KK_APPLE_TEAM_ID,
        'iat': int(timezone.now().timestamp()),
        'exp': int(timezone.now().timestamp())+2592000,
        'aud': 'https://appleid.apple.com',
        'sub': settings.KK_APPLE_CLIENT_ID
    }
    secret = settings.KK_APPLE_KEY
    return jwt.encode(
        payload,
        secret, 
        algorithm='ES256', 
        headers=headers
    )

def get_apple_id_token(token):
    client_secret = create_apple_client_secret()
    
    headers = {'content-type': "application/x-www-form-urlencoded"}
    data = {
        'client_id': settings.KK_APPLE_CLIENT_ID,
        'client_secret': client_secret,
        'code': token,
        'grant_type': 'authorization_code',
        'redirect_uri': settings.KK_APPLE_REDIRECT_URL,
    }

    response = requests.post(APPLE_ACCESS_TOKEN_URL, data=data, headers=headers)
    if response.ok:
        return True, response.json()['id_token']
    else:
        return False, response.json()

def get_apple_user_email(id_token):
    try:
        user = jwt.decode(id_token, options={'verify_signature': False})
    except Exception as e:
        return None
    return user['email']

def generate_jwt(user):
    serializer = TokenObtainPairSerializer()
    token_data = serializer.get_token(user)
    user.last_login = timezone.now()
    user.save()
    access_token = token_data.access_token
    refresh_token = token_data
    return access_token, refresh_token

def login_with_third_party_info(email, provider, first_name=None, last_name=None):
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            register_type=provider,
            is_password_none=True
        )
    return generate_jwt(user)

def google_login(token):
    user_data = get_google_user_info(token)    
    if not user_data:
        return None
    access_token, refresh_token = login_with_third_party_info(
        user_data['email'],
        'google',
        user_data.get('given_name', None),
        user_data.get('family_name', None)
        )

    return {
        'access': str(access_token),
        'refresh': str(refresh_token)
    }

def facebook_login(token):
    user_data = get_facebook_user_data(token)
    if not user_data:
        return None
    access_token, refresh_token = login_with_third_party_info(
        user_data['email'],
        'facebook',
        user_data.get('first_name', None),
        user_data['last_name'].get('last_name', None)
    )

    return {
        'access': str(access_token),
        'refresh': str(refresh_token)
    }

def apple_login(token):
    success, id_token = get_apple_id_token(token)
    if success:
        user_email = get_apple_user_email(id_token)
    else:
        return None
    access_token, refresh_token = login_with_third_party_info(
        user_email,
        'apple'
    )

    return {
        'access': str(access_token),
        'refresh': str(refresh_token)
    }

def generate_random_nonce(length=None):
    if not length:
        length = settings.KK_WEB3_AUTH_NONCE_LENGTH
    return "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(length)
    )

# def verify_singature(wallet_address, nonce, signature):
#     # TODO remove this when test is over
#     if signature == "testsignature":
#         return True
#     try:
#         recovered_message = Web3.eth.account.recover_message(encode_defunct(text=nonce), signature=signature)
#         return recovered_message.lower() == wallet_address.lower()
#     except BadSignature:
#         return False
