'''
Settings specific to Knockknock
'''
from django.conf import settings
from decouple import config

# Specifies if users need to verify their email address via an email
# containing user-specific token or not
settings.KK_REQUIRE_EMAIL_VALIDATION = config(
    "KK_REQUIRE_EMAIL_VALIDATION",
     default=True,
     cast=bool
     )

# Address to which user's should be redirected to in order to activate their account.
# user_id and token will be added to this address as query parameters. For an activation
# url like https://example.com/activation/ the generated link for a specific user would
# be like https://example.com/activation/?u=93929&t=ZtdLljClfrenTkjq393nfeq
settings.KK_ACCOUNT_ACTIVATION_URL = config(
    "KK_ACCOUNT_ACTIVATION_URL",
     default=None
    )

# Address to which user's should be redirected to in order to reset their passwords.
# user_id and token will be added to this address as query parameters. For a password
# reset url like https://example.com/password-reset/ the generated link for a specific user would
# be like https://example.com/password-reset/?u=93929&t=ZtdLljClfrenTkjq393nfeq
settings.KK_PASSWORD_RESET_URL = config(
    "KK_PASSWORD_RESET_URL",
     default=None
    )

# Google auth settings

# Google client ID specified in google api dashboard
settings.KK_ENABLE_GOOGLE_AUTH = config(
    "KK_ENABLE_GOOGLE_AUTH",
    default=False,
    cast=bool
)
settings.KK_GOOGLE_CLIENT_ID = config(
    "KK_GOOGLE_CLIENT_ID",
    default=None
    )

# Google client secret from google api dashboard
settings.KK_GOOGLE_CLIENT_SECRET = config(
    "KK_GOOGLE_CLIENT_SECRET",
    default=None
    )

# Google login confirm url is redirect url registered in your
# google api dashboard
settings.KK_GOOGLE_LOGIN_CONFIRM_URL = config(
    "KK_GOOGLE_LOGIN_CONFIRM_URL",
    default=None
    )

# Facebook auth settings
settings.KK_ENABLE_FACEBOOK_AUTH = config(
    "KK_ENABLE_FACEBOOK_AUTH",
    default=False,
    cast=bool
)
settings.KK_FACEBOOK_CLIENT_ID = config(
    "KK_FACEBOOK_CLIENT_ID",
    default=None
)
settings.KK_FACEBOOK_CLIENT_SECRET = config(
    "KK_FACEBOOK_CLIENT_SECRET",
    default=None
)
settings.KK_FACEBOOK_REDIRECT_URL = config(
    "KK_FACEBOOK_REDIRECT_URL",
    default=None
)

# Apple auth settings
settings.KK_ENABLE_APPLE_AUTH = config(
    "KK_ENABLE_APPLE_AUTH",
    default=False,
    cast=bool
)
settings.KK_APPLE_TEAM_ID = config(
    "KK_APPLE_TEAM_ID",
    default=None
    )
settings.KK_APPLE_CLIENT_ID = config(
    "KK_APPLE_CLIENT_ID",
    default=None
    )
settings.KK_APPLE_KEY = config(
    "KK_APPLE_KEY",
    default=None
    )
settings.KK_APPLE_KEY_ID = config(
    "KK_APPLE_KEY_ID",
    default=None
    )
settings.KK_APPLE_REDIRECT_URL = config(
    "KK_APPLE_REDIRECT_URL",
    default=None
    )
settings.KK_ENABLE_WEB3_AUTH = config(
    "KK_ENABLE_WEB3_AUTH",
    default=False,
    cast=bool
    )
settings.KK_WEB3_AUTH_NONCE_LENGTH = config(
    "KK_WEB3_AUTH_NONCE_LENGTH",
    default=24,
    cast=int
    )