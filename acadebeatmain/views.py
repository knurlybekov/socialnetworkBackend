from audioop import reverse
from datetime import timedelta
from io import BytesIO

from django.contrib.contenttypes.models import ContentType
from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from oauth2_provider.contrib.rest_framework.permissions import TokenHasReadWriteScope, TokenHasScope
from oauth2_provider.models import AccessToken, Application
from oauth2_provider.oauth2_validators import RefreshToken
from oauth2_provider.settings import oauth2_settings
from oauthlib.common import generate_token
from rest_framework import viewsets, status, permissions, generics, request, serializers
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import CustomUserCreationForm, UserChangeForm, PostForm, CommentForm
from .models import User, Post, Comment, Dialogue, Subscription, Like
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .serializers import UserSerializer, RegisterSerializer, LogoutSerializer, PostSerializer, CommentSerializer, \
    DialogueSerializer, SubscriptionSerializer, LikeSerializer
from django.contrib.auth import logout as django_logout
from django.template.loader import get_template



def generate_dialogue_pdf(dialogue_data):
    buffer = BytesIO()
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    print(dialogue_data)
    can.setFont("Helvetica", 12)  # Set default font and size

    y_position = 750  # Starting vertical position for text
    line_height = 20

    # Title
    can.setFont("Helvetica-Bold", 14)
    can.drawString(100, y_position, f"Dialogue {dialogue_data['data']['dialogueId']}")
    y_position -= line_height * 2  # Move down for the next section

    for item in dialogue_data["data"]["dialogue"]["content"]:
        if y_position < 50:  # Check if we need to add a new page
            can.showPage()
            y_position = 750  # Reset y_position for the new page

        # Name (bolded)
        can.setFont("Helvetica-Bold", 12)
        can.drawString(100, y_position, f"{item['name']}:")
        y_position -= line_height

        # Content
        can.setFont("Helvetica", 12)
        can.drawString(120, y_position, item["content"])
        y_position -= line_height  # Move down for the next line

    can.save()

    packet.seek(0)
    new_pdf = PdfReader(packet)
    page = new_pdf.pages[0]

    output = PdfWriter()
    output.add_page(page)
    output.write(buffer)
    buffer.seek(0)

    return buffer


def health(request):
    # Basic Status Check (200 OK)
    # status = 200
    # response_data = {"status": "ok"}
    return HttpResponse(status=200)


class DialogueCreateAPIView(generics.CreateAPIView):
    queryset = Dialogue.objects.all()
    serializer_class = DialogueSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            dialogueId = serializer.validated_data['dialogueId']
            existing_dialogue = Dialogue.objects.filter(dialogueId=dialogueId).first()

            if existing_dialogue:
                existing_dialogue.data = serializer.validated_data['data']
                existing_dialogue.save()
            else:
                self.perform_create(serializer)

            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DialogueUpdateAPIView(generics.UpdateAPIView):
    queryset = Dialogue.objects.all()
    serializer_class = DialogueSerializer

    def update(self, request, *args, **kwargs):
        return HttpResponse(status=200)


class DialogueDeleteAPIView(generics.DestroyAPIView):
    queryset = Dialogue.objects.all()
    serializer_class = DialogueSerializer

    def delete(self, request, *args, **kwargs):
        return HttpResponse(status=200)


class DialogueListAPIView(generics.ListAPIView):
    queryset = Dialogue.objects.all()
    serializer_class = DialogueSerializer

    def get_queryset(self):
        return Dialogue.objects.all()


class DialogueRetrieveAPIView(viewsets.ViewSet):
    queryset = Dialogue.objects.all()
    serializer_class = DialogueSerializer

    def get_object(self, pk):
        try:
            return Dialogue.objects.get(pk=pk)
        except Dialogue.DoesNotExist:
            raise Http404

    def retrieve(self, request, pk=None):
        dialogue = self.get_object(pk)
        serializer = self.serializer_class(dialogue)
        return Response(serializer.data)

    def download(self, request, pk=None):
        # Get the dialogue object
        dialogue = self.get_object(pk)
        serializer = self.serializer_class(dialogue)
        data = serializer.data

        # Generate the PDF
        pdf_buffer = generate_dialogue_pdf(data)

        # Create the response
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="dialogue_{dialogue.pk}.pdf"'
        return response


class GetUserProfileAPIView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# @api_view(['POST'])
# def login(request):
#     user = get_object_or_404(User, email=request.data['email'])
#     if not user.check_password(request.data['password']):
#         return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
#     token, created = Token.objects.get_or_create(user=user)
#     serializer = UserSerializer(instance=user)
#     return Response({'token': token.key, "user": serializer.data})


@api_view(['POST'])
def signup(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(email=request.data['email'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({'token': token.key, "user": serializer.data})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        print(f"Received email: {email}, password: {password}")
        user = authenticate(request, username=email, password=password)
        print(f"Authenticated user: {user}")
        from oauth2_provider.models import Application
        print(Application.objects.filter(name="authapp").exists())
        if user is not None:
            login(request, user)

            # Generate OAuth2 token
            try:
                application = Application.objects.get(name="authapp")
            except Application.DoesNotExist:
                return Response({'detail': 'OAuth2 application not found'},
                                status=500)  # Or another appropriate error status
            # application = Application.objects.get(name="authapp")  # Replace with your app name
            expires = timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)
            access_token = AccessToken.objects.create(
                user=user,
                scope='read write',
                expires=expires,
                token=generate_token(),  # You'll need to implement this function
                application=application
            )

            return Response({
                'access_token': access_token.token,
                'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS,
                'token_type': 'Bearer',
                'scope': access_token.scope,
            })

        else:
            return Response({'detail': 'Invalid credentials'}, status=401)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = request.data.get('token')  # Get the token from the POST request

            if token is None:
                return Response({'error': 'No token provided'}, status=400)

            access_token = AccessToken.objects.get(token=token)
            access_token.revoke()
            django_logout(request)
            return Response({'message': 'Logout successful'}, status=200)
        except AccessToken.DoesNotExist:
            return Response({'error': 'Invalid token'}, status=400)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed for {}".format(request.user.email))


class EditProfileView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


# Profile Update View
# class EditProfileView(generics.UpdateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get_object(self):
#         return self.request.user


# class UserSearchView(generics.ListAPIView):
#     permission_classes = [permissions.IsAuthenticated]  # Requires authentication
#     serializer_class = UserSerializer  # Specify the serializer for user data
#
#     def get_queryset(self):
#         """Filters users based on the query parameter."""
#         query = self.request.query_params.get('q', '')  # Get the 'q' query param
#         if query:
#             return User.objects.filter(
#                 Q(username__icontains=query) |
#                 Q(email__icontains=query) |
#                 Q(first_name__icontains=query) |
#                 Q(last_name__icontains=query)
#             ).distinct()
#         return User.objects.none()  # Return empty queryset if no query


# search is very questionable
class UserSearchPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserSearchView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    pagination_class = UserSearchPagination

    def get_queryset(self):
        query = self.request.query_params.get('q', '')  # Get the 'q' query parameter
        if not query:
            return User.objects.all()

        return User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).distinct()



# Search Results View
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def search_results(request):
#     query = request.GET.get('q', '')
#     if query:
#         results = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))
#         serializer = UserSerializer(results, many=True)
#         return Response(serializer.data)
#     return Response([])


# Follow and Unfollow Views
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def follow(request):
#     following_user_id = request.data.get('following_user_id')
#     try:
#         user_to_follow = User.objects.get(id=following_user_id)
#         _, created = UserFollowing.objects.get_or_create(user_id=request.user, following_user_id=user_to_follow)
#         return Response({'success': True, 'created': created})
#     except User.DoesNotExist:
#         return Response({'success': False, 'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
# class FollowView(generics.CreateAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     serializer_class = UserFollowingSerializer
#
#     def perform_create(self, serializer):
#         try:
#             user_to_follow = User.objects.get(id=self.request.data['following_user_id'])
#             serializer.save(user_id=self.request.user, following_user_id=user_to_follow)
#         except User.DoesNotExist:
#             raise serializers.ValidationError({'error': 'User not found.'})
#
#
# class UnfollowView(generics.DestroyAPIView):
#     permission_classes = [permissions.IsAuthenticated]
#     queryset = UserFollowing.objects.all()
#
#     def perform_destroy(self, instance):
#         if instance.user_id != self.request.user:
#             raise PermissionError("You cannot unfollow someone else's relationship.")
#         instance.delete()
#
#     def delete(self, request, *args, **kwargs):
#         try:
#             return super().delete(request, *args, **kwargs)
#         except UserFollowing.DoesNotExist:
#             return Response({'success': False, 'error': 'Relationship not found.'}, status=status.HTTP_404_NOT_FOUND)
#         except PermissionError as e:
#             return Response({'success': False, 'error': str(e)}, status=status.HTTP_403_FORBIDDEN)

# untested
# class FollowView(viewsets.ViewSet):
#     queryset = User.objects.all()
#
#     def follow(self, request, pk):
#         serializer = FollowSerializer(data={'user_id': pk})
#         if serializer.is_valid():
#             response_data = serializer.follow(request.user)
#             return Response(response_data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def unfollow(self, request, pk):
#         serializer = FollowSerializer(data={'user_id': pk})
#         if serializer.is_valid():
#             response_data = serializer.unfollow(request.user)
#             return Response(response_data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#


#
#
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def unfollow(request):
#     following_user_id = request.data.get('following_user_id')
#     try:
#         user_to_unfollow = User.objects.get(id=following_user_id)
#         UserFollowing.objects.filter(user_id=request.user, following_user_id=user_to_unfollow).delete()
#         return Response({'success': True})
#     except User.DoesNotExist:
#         return Response({'success': False, 'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


# Post stuff, done
class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(postauthor=self.request.user)


class PostListView(generics.ListAPIView):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.all()


class AllPostsByUserId(generics.ListAPIView):
    queryset = Post.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PostSerializer

    def get_queryset(self):
        return Post.objects.filter(postauthor=self.kwargs['pk'])


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Post.objects.get(pk=self.kwargs['pk'])


# Comment stuff, done. Need to show the comments under the posts
class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['pk'])
        serializer.save(author=self.request.user, post=post)


# Like and Unlike Post View
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def like_unlike_post(request):
#     post_id = request.data.get('post_id')
#     action = request.data.get('action')
#
#     try:
#         post = Post.objects.get(id=post_id)
#         if action == 'like':
#             post.likes.add(request.user)
#         elif action == 'unlike':
#             post.likes.remove(request.user)
#         return Response({'success': True, 'likes_count': post.likes.count()})
#     except Post.DoesNotExist:
#         return Response({'success': False, 'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

# questionable and untested
class LikeUnlikePostView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def update(self, request, *args, **kwargs):
        post = self.get_object()
        action = request.data.get('action')

        if action == 'like':
            post.likes.add(request.user)
        elif action == 'unlike':
            post.likes.remove(request.user)
        else:
            return Response({'success': False, 'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': True, 'likes_count': post.likes.count()}, status=status.HTTP_200_OK)


#
# # Add Comment View
# @api_view(['POST'])
# @permission_classes([permissions.IsAuthenticated])
# def add_comment(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     serializer = CommentSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save(author=request.user, post=post)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# subscriptions stuff, somehow works
class CreateSubscriptionAPIView(generics.CreateAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        subscribed_to_user = get_object_or_404(User, pk=self.kwargs['pk'])

        if Subscription.objects.filter(subscriber=self.request.user, subscribed_to=subscribed_to_user).exists():
            return Response({'error': 'You are already subscribed to this user.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(subscriber=self.request.user, subscribed_to=subscribed_to_user)


class DeleteSubscriptionAPIView(generics.DestroyAPIView):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        subscribed_to_user = get_object_or_404(User, pk=self.kwargs['pk'])
        return get_object_or_404(Subscription, subscriber=self.request.user, subscribed_to=subscribed_to_user)


class ListSubscriptionsAPIView(generics.ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(subscriber=self.request.user)


class CreateLikeAPIView(generics.CreateAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):

        content_type = get_object_or_404(ContentType, model=self.kwargs['content_type'])
        obj = get_object_or_404(content_type.model_class(), pk=self.kwargs['object_id'])

        if Like.objects.filter(user=self.request.user, content_type=content_type, object_id=obj.id).exists():
            return Response({'error': 'You have already liked this.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(user=self.request.user, content_object=obj)


class DeleteLikeAPIView(generics.DestroyAPIView):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_object(self):
        content_type = get_object_or_404(ContentType, model=self.kwargs['content_type'])
        obj = get_object_or_404(content_type.model_class(), pk=self.kwargs['object_id'])
        return get_object_or_404(Like, user=self.request.user, content_type=content_type, object_id=obj.id)


class PostLikesAPIView(generics.ListAPIView):
    serializer_class = LikeSerializer

    def get_queryset(self):
        post_id = self.kwargs['post_id']
        post = get_object_or_404(Post, id=post_id)
        content_type = ContentType.objects.get_for_model(Post)
        return Like.objects.filter(content_type=content_type, object_id=post.id)