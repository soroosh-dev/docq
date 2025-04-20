from django.urls import path
from rest_framework_simplejwt import views as jwt_views
# from .views import UserAPIView, ActivateUserAPIView, Login, PasswordResetAPIView, Web3LoginAPIView, Web3NonceAPIView, Web3ConnectWalletAPIView, UserSearchAPIView
from .views import UserAPIView, ActivateUserAPIView, Login, PasswordResetAPIView, UserSearchAPIView
from .settings import settings

urlpatterns = [
    path('', UserAPIView.as_view(), name='user'),
    path('token/', Login.as_view(), name='login'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token-refresh'),
    path('token/verify/', jwt_views.TokenVerifyView.as_view(), name='token-verify'),
    path('password_reset/', PasswordResetAPIView.as_view(), name='password-rest'),
    path('activate/', ActivateUserAPIView.as_view(), name='activation'),
    path('users/', UserSearchAPIView.as_view(), name='user-list'),
]

# if settings.KK_ENABLE_WEB3_AUTH:
#     urlpatterns += [
#         path("nonce/<str:address>/", Web3NonceAPIView.as_view(), name='get-nonce'),
#         path("web3auth/", Web3LoginAPIView.as_view(), name='web3-auth'),
#         path("wallet/", Web3ConnectWalletAPIView.as_view(), name='wallet'),
#     ]