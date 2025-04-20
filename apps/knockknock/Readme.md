# KnockKnock
Simple JWT authentication api library, providing authentication via google, facebook and apple.

## Simple usage guide
By following these steps you can use simply add authentication to your django project.
If you wish to customize user model you should inherit your user model from `knockknock.models.User`. You might also need to implement your own views and serializers but you can use View and Serializer classes defined in KnockKnock as a starting point.

**Note** We assume this library is stored at `project_root/apps/knockknock` for the rest of this document.

### Install dependencies.
Run the following command from your project's root directory to install the required dependencies.
```sh
pip install -r apps/knockknock/requirements.txt
```

**Note** KnockKnock relies on celery for sending email verification and password reset emails. So you should configure celery in your project.

### settings.py
Apply the following changes to your project's `settings.py` file.
- Add `apps.knockknock` to `INSTALLED_APPS`.
- Add `AUTH_USER_MODEL = 'knockknock.user'`.

### urls.py
Include `apps.knockknock.urls` in your main `urls.py` file and route it to your desired path.

Example:
```python
urlpatterns = [
     path('api/v1/', include('apps.knockknock.urls')),
     ...
]
```
Paths included in `knockknock.urls` are as follows:
- `user/` - `POST` method: Register user
- `user/` - `GET` method: Returns currently logged in user's information.
- `user/` - `PUT` method: Updates currently logged in user's information.
- `token/` - `POST` method: Returns JWT tokens if credentials sent via request data are valid.
- `token/` - `GET` method: Returns JWT tokens if provided thirdparty token is valid.
- `token/refresh/` - `POST` method: Gets refresh token and generates a new access token.
- `token/verify/` - `POST` method: Gets a token and tells if it is valid or not.
- `user/password_reset/` - `GET` method: Generates a password reset token and sends it to user via email.
- `user/password_reset/` - `POST` method: Gets userID, password reset token and new password and sets new password for the user upon token validation.
- `user/activate/` - `GET` method: Gets userID and activation token and activates the user upon token validation.

### .env
Add the following environment variables to your .env file and set their values according to the settings for each third-party authenticator you wish to use.

```
# KnockKnock settings
KK_REQUIRE_EMAIL_VALIDATION=false
KK_ACCOUNT_ACTIVATION_URL=
KK_PASSWORD_RESET_URL=

# KnockKnock googleauth settings
KK_ENABLE_GOOGLE_AUTH=false
KK_GOOGLE_CLIENT_ID=
KK_GOOGLE_CLIENT_SECRET=
KK_GOOGLE_LOGIN_CONFIRM_URL=

# KnockKnock facebookauth settings
KK_ENABLE_FACEBOOK_AUTH=false
KK_FACEBOOK_CLIENT_ID=
KK_FACEBOOK_CLIENT_SECRET=
KK_FACEBOOK_REDIRECT_URL=

# KnockKnock apple auth settings
KK_ENABLE_APPLE_AUTH=false
KK_APPLE_TEAM_ID=
KK_APPLE_CLIENT_ID=
KK_APPLE_KEY_ID=
KK_APPLE_KEY=-----BEGIN PRIVATE KEY-----\nHy34XMG9/3QfByqGSM49AgEGCCqGSM49AwEHBHkwdwIBAQQg1uvfbTxtHTGak5L+\ngGjJNaaqDj5BRz8Fve4jr0S8KBWgCgYIKoZIzj0DAQehRANCTTE1SM78Jx6EIVa3\nhayiBiX1AFh2MBmWww5V81orhe2QS/2GmKb11kuHTcIXu0uJG4/6xLSTWVgtcLis\nC6kqQkX1\n-----END PRIVATE KEY-----
KK_APPLE_REDIRECT_URL=

# Knockknock web3 auth settings
KK_ENABLE_WEB3_AUTH=true
KK_WEB3_AUTH_NONCE_LENGTH=24

```

**Note** Remember that `KK_APPLE_KEY` variable should start with `-----BEGIN PRIVATE KEY-----` following with a newline(`\n`)character and every 64 character of the key should also be seperated with a newline character. It should also end with `-----END PRIVATE KEY-----`.

### Run migrations
From your project's root directory run the following command:
```sh
python manage.py migrate
```
