import os

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from .models import User, Comment, Post, UserFollowing, Dialogue


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
        extra_kwargs = {'password': {'write_only': True, 'required': True}}

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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    postauthor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'postauthor', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'content', 'created_at']

class UserFollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFollowing
        fields = ['user_id', 'following_user_id']




# class DialogueMessageSerializer(serializers.Serializer):
#     name = serializers.CharField()
#     imagePath = serializers.CharField()
#     id = serializers.CharField()  # Assuming these IDs are strings
#     content = serializers.CharField()
#
# class DialogueSerializer(serializers.Serializer):
#     dialogueId = serializers.CharField()
#     dialogue = DialogueMessageSerializer(many=True)
#
#     class Meta:
#         model = Dialogue
#         fields = ['dialogueId', 'dialogue']
#
#
#
# class DialogueExampleSerializer(serializers.ModelSerializer):
#     detail_json_formatted = serializers.SerializerMethodField()  # Read-only field
#
#     class Meta:
#         model = DialogueExample
#         fields = ['dialogue_id', 'detail_json']  # Include all fields, or specify a subset
#         # read_only_fields = ['id']  # Prevent client from setting 'id'
#
#     def get_detail_json_formatted(self, obj):
#         return obj.detail_json_formatted()
#
class DialogueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dialogue
        fields = ['dialogueId', 'created_by', 'data']

