import os

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import User

# class GoogleSocialAuthSerializer(serializers.Serializer):
#     auth_token = serializers.CharField()
#     def validate_auth_token(self, auth_token):
#         user_data = google.Google.validate(auth_token)
#         try:
#             user_data['sub']
#         except:
#             raise serializers.ValidationError('The token is invalid or expired. Please login again')
#         if user_data['aud'] != os.environ.get('GOOGLE_CLIENT_ID'):
#             raise AuthenticationFailed('Who are you?')
#
#         user_id = user_data['sub']
#         email= user_data['email']
#         name = user_data['name']
#         provider = 'google'
#         return register_social_user(provider=provider, email=email, user_id=user_id, name=name)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'date_of_birth')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user


class LogoutSerializer(serializers.Serializer):
    token = serializers.CharField()