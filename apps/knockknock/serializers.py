from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .settings import settings
from .models import User
from .tokens import RegisterTokenGenerator


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']
        read_only_fields = ['id', 'username', 'first_name', 'last_name']

class UserPostSerializer(serializers.ModelSerializer):
    '''
    Serializer used to register a new user.
    '''
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['date_joined']
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': False}
            }

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise exc
        return value

    def create(self, validated_data):
        if not validated_data.get('username', None):
            validated_data['username'] = validated_data['email']
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        if settings.KK_REQUIRE_EMAIL_VALIDATION:
            user.is_active = False
        else:
            user.is_active = True
        user.register_type = "API"
        user.save()
        return user

class UserInfoSerializer(UserPostSerializer):
    '''
    Serializer for returning a user in response or
    updating an existing user.
    '''
    old_password = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'old_password', 'date_joined']
        read_only_fields = ['date_joined', 'id', 'username']

    def validate(self, attrs):
        if 'password' in attrs.keys() and not 'old_password' in attrs.keys():
            raise serializers.ValidationError(
                {'old_password': "You must provide your old password in order to update it."}
                )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        if validated_data.get('email', None):
            # if instance.email:
            #     raise serializers.ValidationError(
            #         {"email": "email can not be modified."}
            #     )
            instance.email = validated_data['email']
        if validated_data.get('password', None):
            if instance.is_password_none or instance.check_password(validated_data.get('old_password')):
                instance.set_password(validated_data.get('password'))
                instance.is_password_none = False
            else:
                raise serializers.ValidationError(
                    {"old_password": "Provided old password is not valid."}
                    )
        if validated_data.get('first_name', None):
            instance.first_name = validated_data.get('first_name')
        if validated_data.get('last_name', None):
            instance.last_name = validated_data.get('last_name')
        instance.save()
        return instance

class ActivationRequestSerializer(serializers.Serializer):
    '''
    Serializer for account activation view.
    '''
    u = serializers.IntegerField() # user_id
    t = serializers.CharField() # token

    def validate(self, attrs):
        if not super().validate(attrs):
            return False
        try:
            user = User.objects.get(pk=attrs['u'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid user_id and token pair.')
        token_generator = RegisterTokenGenerator()
        if not token_generator.check_token(user, attrs['t']):
            raise serializers.ValidationError('Invalid user_id and token pair.')
        attrs['user'] = user
        return attrs

class PasswordResetRequestSerializer(serializers.Serializer):
    '''
    Serializer for requesting password reset link.
    '''
    email = serializers.EmailField()

    def validate(self, attrs):
        if not super().validate(attrs):
            return False
        try:
            user = User.objects.get(email=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Provided email does not belong to any user.')
        return attrs

class PasswordResetSerializer(serializers.Serializer):
    '''
    Serializer for password reset view.
    '''
    user_id = serializers.IntegerField()
    token = serializers.CharField()
    password = serializers.CharField()

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as exc:
            raise exc
        return value

    def validate(self, attrs):
        if not super().validate(attrs):
            return False
        try:
            user = User.objects.get(pk=attrs['user_id'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Invalid user_id and token pair.')
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, attrs['token']):
            raise serializers.ValidationError('Invalid user_id and token pair.')
        return attrs

class ThirdPartyTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    provider = serializers.ChoiceField(choices=['google', 'apple', 'facebook'])

class GetNonceRequestSerializer(serializers.Serializer):
    address = serializers.CharField()

    def validate_address(self, value):
        value = super.validate_address(value)
        return value.lower()

class Web3LoginRequestSerializer(serializers.Serializer):
    address = serializers.CharField()
    signature = serializers.CharField()

    def validate_address(self, value):
        return value.lower()

