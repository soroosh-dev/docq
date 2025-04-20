from datetime import timedelta
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt import views as jwt_views
from .models import User, Web3Auth
from . import utils, tasks, permissions as custom_permissions
from .serializers import UserInfoSerializer, UserPostSerializer, ActivationRequestSerializer, ThirdPartyTokenSerializer, PasswordResetRequestSerializer, PasswordResetSerializer, GetNonceRequestSerializer, Web3LoginRequestSerializer, UserPublicSerializer
from .settings import settings

class UserSearchAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        search_text = request.query_params.get('search', None)
        queryset = User.objects.filter(is_active=True, is_staff=False).exclude(id=request.user.id)
        if search_text:
            queryset = queryset.filter(Q(username__icontains=search_text) | Q(first_name__icontains=search_text) | Q(last_name__icontains=search_text))
        return Response(UserPublicSerializer(queryset[:50], many=True).data, status=status.HTTP_200_OK)


class UserAPIView(APIView):
    '''
    API View responsible for user CRUD operations.
    '''
    permission_classes = [custom_permissions.IsAuthenticatedOrCreateOnly]

    def post(self, request, format=None):
        serializer = UserPostSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if settings.KK_REQUIRE_EMAIL_VALIDATION:
                tasks.send_user_activation_email.apply_async(args=[user.id])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        serializer = UserInfoSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, format=None):
        serializer = UserInfoSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActivateUserAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        serializer = ActivationRequestSerializer(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data['user']
            user.is_active = True
            user.save()
            return Response({}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, format=None):
        '''
        Generates a password reset token and sends it to user's email.
        '''
        serializer = PasswordResetRequestSerializer(data=request.query_params)
        if serializer.is_valid(raise_exception=True):
            tasks.send_password_reset_email.apply_async(args=[serializer.validated_data['email']])
            return Response({}, status=status.HTTP_202_ACCEPTED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, format=None):
        '''
        Gets a user's ID and a password reset token via query params and
        new password via request data. Sets new password for user upon token's
        validation.
        '''
        input_data = {
            'user_id': request.query_params.get("user_id", None),
            'token': request.query_params.get("token", None),
            'password': request.data.get("password", None)
        }
        serializer = PasswordResetSerializer(data=input_data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = User.objects.get(pk=serializer.validated_data['user_id'])
            except User.DoesNotExist:
                return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            user.set_password(serializer.validated_data['password'])
            user.is_password_none = False
            user.save()
            return Response({}, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Login(jwt_views.TokenObtainPairView):

    def get(self, request, format=None):
        '''
        Recieves third-party token and token provider to authenticate
        a user or register in the local databse.
        '''
        serializer = ThirdPartyTokenSerializer(data=request.query_params)
        if serializer.is_valid():
            if settings.KK_ENABLE_GOOGLE_AUTH and serializer.validated_data['provider'] == 'google':
                tokens = utils.google_login(serializer.validated_data['token'])
                if not tokens:
                    return Response({"error": "Login via google failed."}, status.HTTP_401_UNAUTHORIZED)
            elif settings.KK_ENABLE_FACEBOOK_AUTH and serializer.validated_data['provider'] == 'facebook':
                tokens = utils.facebook_login(serializer.validated_data['token'])
                if not tokens:
                    return Response({"error": "Login via facebook failed."}, status.HTTP_401_UNAUTHORIZED)
            elif settings.KK_ENABLE_APPLE_AUTH and serializer.validated_data['provider'] == 'apple':
                tokens = utils.apple_login(serializer.validated_data['token'])
                if not tokens:
                    return Response({"error": "Login via apple failed."}, status.HTTP_401_UNAUTHORIZED)
            else:
                return Response({"error": "Invalid provider."}, status.HTTP_401_UNAUTHORIZED)
            return Response(tokens)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class Web3NonceAPIView(APIView):
#     permission_classes = [permissions.AllowAny]
#     #TODO Add throttle

#     def get(self, request, address, *args, **kwargs):
#         address = address.lower()
#         # TODO validate if address is a proper address
#         try:
#             wallet = Web3Auth.objects.get(address=address)
#             wallet.nonce = utils.generate_random_nonce()
#             wallet.save()
#         except Web3Auth.DoesNotExist:
#             user = User.objects.create(
#             username=address,
#                 is_password_none=True,
#                 register_type="web3"
#             )
#             wallet = Web3Auth.objects.create(
#                 user=user,
#                 address=address,
#                 nonce=utils.generate_random_nonce()
#             )

#         return Response({
#             "address": wallet.address,
#             "nonce": wallet.nonce
#         }, status=status.HTTP_200_OK)

# class Web3LoginAPIView(APIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request, *args, **kwargs):
#         serializer = Web3LoginRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 wallet = Web3Auth.objects.get(address=serializer.validated_data['address'])
#                 if utils.verify_singature(wallet.address, wallet.nonce, serializer.validated_data['signature']) and wallet.refreshed_at > timezone.now()-timedelta(minutes=10):
#                     access_token, refresh_token =  utils.generate_jwt(wallet.user)
#                     return Response({
#                         "access": str(access_token),
#                         "refresh": str(refresh_token)
#                     }, status=status.HTTP_200_OK)
#             except:
#                 pass
#             return Response({"error": "Invalid credentials."}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class Web3ConnectWalletAPIView(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         try:
#             wallet_address = request.user.wallet.address
#         except:
#             wallet_address = ''
#         return Response({"address": wallet_address}, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
#         nonce = utils.generate_random_nonce()
#         cache.set(f"kk-wallet-nonce-{request.user.id}", nonce, 10*60)
#         return Response({
#             "nonce": nonce
#         }, status=status.HTTP_200_OK)

#     def put(self, request, *args, **kwargs):
#         serializer = Web3LoginRequestSerializer(data=request.data)
#         if serializer.is_valid():
#             nonce = cache.get(f"kk-wallet-nonce-{request.user.id}", None)
#             if nonce and utils.verify_singature(serializer.validated_data['address'].lower(), nonce, serializer.validated_data['signature']):
#                 Web3Auth.objects.create(
#                     address=serializer.validated_data['address'].lower(),
#                     user=request.user,
#                     nonce=nonce
#                 )
#                 return Response({}, status=status.HTTP_200_OK)
#             return Response({"error": "Failed to verify signature"}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
