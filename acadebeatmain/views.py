from audioop import reverse
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from oauth2_provider.oauth2_validators import RefreshToken
from rest_framework import viewsets, status, permissions, generics
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import CustomUserCreationForm, UserChangeForm, PostForm, CommentForm
from .models import User, Post, UserFollowing, SomePost, Comment, Dialogue
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .serializers import UserSerializer, RegisterSerializer, LogoutSerializer, PostSerializer, CommentSerializer, \
    DialogueSerializer


def health(request):
    # Basic Status Check (200 OK)
    status = 200
    response_data = {"status": "ok"}

    # AWS-Specific Checks
    try:
        import boto3  # Check if Boto3 is available
        response_data["aws_sdk"] = "ok"

        # Check Database Connection (if using RDS)
        from django.db import connection
        if connection.is_usable():
            response_data["database"] = "ok"
        else:
            status = 500  # Internal Server Error
            response_data["database"] = "error"
            response_data["message"] = "Database connection failed"

        # Example: Check S3 Bucket Connection (if relevant)
        s3 = boto3.client('s3')
        s3.list_buckets()
        response_data["s3"] = "ok"

    except Exception as e:  # Catch general AWS errors
        status = 500
        response_data["aws_sdk"] = "error"
        response_data["message"] = f"AWS error: {e}"

    return JsonResponse(response_data, status=status)

class DialogueCreateAPIView(generics.CreateAPIView):
    queryset = Dialogue.objects.all()
    serializer_class = DialogueSerializer

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

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        except Dialogue.DoesNotExist:
            return Response({'error': 'Dialogue not found'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login(request):
    user = get_object_or_404(User, email=request.data['email'])
    if not user.check_password(request.data['password']):
        return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({'token': token.key, "user": serializer.data})


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


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout_view(request):
#     try:
#         refresh_token = request.data["refresh_token"]
#         token = RefreshToken(refresh_token)
#         token.blacklist()
#         return Response({"message": "Successfully logged out."}, status=205)
#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response("passed for {}".format(request.user.email))


# Profile Update View
class EditProfileView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# Search Results View
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def search_results(request):
    query = request.GET.get('q', '')
    if query:
        results = User.objects.filter(Q(username__icontains=query) | Q(email__icontains=query))
        serializer = UserSerializer(results, many=True)
        return Response(serializer.data)
    return Response([])


# Follow and Unfollow Views
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def follow(request):
    following_user_id = request.data.get('following_user_id')
    try:
        user_to_follow = User.objects.get(id=following_user_id)
        _, created = UserFollowing.objects.get_or_create(user_id=request.user, following_user_id=user_to_follow)
        return Response({'success': True, 'created': created})
    except User.DoesNotExist:
        return Response({'success': False, 'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unfollow(request):
    following_user_id = request.data.get('following_user_id')
    try:
        user_to_unfollow = User.objects.get(id=following_user_id)
        UserFollowing.objects.filter(user_id=request.user, following_user_id=user_to_unfollow).delete()
        return Response({'success': True})
    except User.DoesNotExist:
        return Response({'success': False, 'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


# Post Create and Detail Views
class PostCreateView(generics.CreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, postauthor=self.request.user)


class PostDetailView(generics.RetrieveAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]


# Comment Create View
class CommentCreateView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        serializer.save(author=self.request.user, post=post)


# Like and Unlike Post View
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_unlike_post(request):
    post_id = request.data.get('post_id')
    action = request.data.get('action')

    try:
        post = Post.objects.get(id=post_id)
        if action == 'like':
            post.likes.add(request.user)
        elif action == 'unlike':
            post.likes.remove(request.user)
        return Response({'success': True, 'likes_count': post.likes.count()})
    except Post.DoesNotExist:
        return Response({'success': False, 'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)


# Add Comment View
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(author=request.user, post=post)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def retrieve_dialogues_from_storage(resource_id):
    # Simulating dialogue storage (replace with your actual logic)
    dialogue_storage = {
        "1": [
            {"name": "Mark", "imagePath": "...", "id": "3", "content": "Hello!"},
            # ... more messages ...
        ]
    }
    return dialogue_storage.get(resource_id, [])  # Return empty list if not found


# class DialogueExampleViewSet(viewsets.ModelViewSet):
#     queryset = DialogueExample.objects.all()
#     serializer_class = DialogueExampleSerializer
#     permission_classes = [permissions.IsAuthenticated]  # Or any other permission
#
#     def perform_create(self, serializer):
#         serializer.save()  # You can add any custom logic here before saving
#
# class DialogueViewSet(viewsets.ViewSet):
#     def create(self, request):
#         serializer = DialogueSerializer(data=request.data)
#         if serializer.is_valid():
#             if hasattr(serializer, 'save'):
#                 serializer.save()
#             else:
#              return Response(serializer.data, status=201)
#         return Response(serializer.errors, status=400)

    # def retrieve(self, request, pk=None):
    #     try:
    #         if hasattr(DialogueSerializer, 'Meta') and hasattr(DialogueSerializer.Meta, 'model'):
    #             dialogue = DialogueSerializer.Meta.model.objects.get(pk=pk)
    #         else:
    #          serializer = DialogueSerializer(dialogue)
    #          return Response(serializer.data)
    #     except (Dialogue.DoesNotExist, KeyError):
    #         return Response(status=status.HTTP_404_NOT_FOUND)
    #
    # def list(self, request):
    #     resource_id = request.query_params.get('resourceId')
    #     if resource_id:
    #         try:
    #             if hasattr(DialogueSerializer, 'Meta') and hasattr(DialogueSerializer.Meta, 'model'):
    #                 dialogues = Dialogue.objects.filter(resource_id=resource_id)
    #             else:
    #                 # Your custom logic to retrieve dialogues without a model
    #                 # For example:
    #                 dialogues = retrieve_dialogues_from_storage(resource_id)
    #
    #             serializer = DialogueSerializer(dialogues, many=True)
    #             return Response(serializer.data)
    #         except KeyError:  # Handle the case where the resource_id doesn't exist
    #             return Response(status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         return Response({"error": "resourceId is required"}, status=status.HTTP_400_BAD_REQUEST)




# @api_view(['POST'])
# def savejson(self, request):
#     data = request.POST.get('data')
#     if data:
#         my_model = dialogjsonmodel.objects.create(data=data)
#         return JsonResponse({'status': 'success', 'id': my_model.id})
#     return JsonResponse({'status': 'error', 'message': 'No data provided'})
#
#
# @api_view(['GET'])
# def getjson(self, request, *args, **kwargs):
#     my_model = dialogjsonmodel.objects.all().values('data', 'created_at', 'updated_at')
#     data = list(my_model)
#     return JsonResponse(data, safe=False)

# class GoogleSocialAuthView(GenericAPIView):
#     serializer_class = GoogleSocialAuthSerializer
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         data = ((serializer.validated_data)['auth-token'])
#         return Response(data, status=status.HTTP_200_OK)

# def home(request):
# if request.user.is_authenticated:
#     followed_users = UserFollowing.objects.filter(user_id=request.user).values_list('following_user_id', flat=True)
#     posts = Post.objects.filter(postauthor_id__in=followed_users).order_by('-timestamp')
# else:
#     posts = Post.objects.all().order_by('-timestamp')  # Show all posts if not logged in
#
# return render(request, 'home.html', {'posts': posts})

# def signup(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect(reverse('login'))  # Redirect to login page after signup
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'signup.html', {'form': form})
#
#
# @login_required
# def user_profile(request, user_id):
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         raise Http404("User not found")
#
#     posts = Post.objects.filter(postauthor_id=user_id)  # Filter by postauthor_id
#     return render(request, 'user_profile.html', {'user': user, 'posts': posts})

# class addpost(generic.CreateView):
#     template_name = 'create_post.html'


# def user_login(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         user = authenticate(request, username=email, password=password)
#         if user is not None:
#             login(request, user)
#             return redirect('profile')  # Redirect to a success page.
#         else:
#             return render(request, 'login.html', {'error': 'Invalid email or password'})
#     else:
#         return render(request, 'login.html')


# def edit_profile(request):
#     if request.method == 'POST':
#         form = UserChangeForm(request.POST, request.FILES, instance=request.user)
#         if form.is_valid():
#             form.save()
#             return redirect('user_profile', user_id=request.user.id)  # Redirect to the profile page
#     else:
#         form = UserChangeForm(instance=request.user)
#     return render(request, 'edit_profile.html', {'form': form})
#
#
# @login_required
# def search_results(request):
#     query = request.GET.get('q')
#     results = None
#     followed_user_ids = []
#
#     if query:
#         results = User.objects.filter(
#             Q(username__icontains=query) | Q(email__icontains=query)
#         )
#
#         if request.user.is_authenticated:
#             followed_user_ids = UserFollowing.objects.filter(
#                 user_id=request.user
#             ).values_list('following_user_id', flat=True)
#
#         for user in results:
#             user.is_followed = user.id in followed_user_ids
#             user.full_name = user.get_full_name()
#
#     return render(request, 'search_results.html', {'results': results, 'query': query})
#
#
# @login_required
# @require_POST
# def follow(request):
#     following_user_id = request.POST.get('following_user_id')
#     try:
#         user_to_follow = User.objects.get(id=following_user_id)
#         _, created = UserFollowing.objects.get_or_create(user_id=request.user, following_user_id=user_to_follow)
#         return JsonResponse({'success': True, 'created': created})
#     except User.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'User not found.'})
#
#
# @login_required
# @require_POST
# def unfollow(request):
#     following_user_id = request.POST.get('following_user_id')
#     try:
#         user_to_unfollow = User.objects.get(id=following_user_id)
#         UserFollowing.objects.filter(user_id=request.user, following_user_id=user_to_unfollow).delete()
#         return JsonResponse({'success': True})
#     except User.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'User not found.'})
# class PostCreateView(LoginRequiredMixin, CreateView):
#     model = Post
#     form_class = PostForm
#
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         response = super().form_valid(form)  # Save the post first
#         form.save_m2m()  # Save the tags (important for TaggableManager)
#         return response
#
#
# class CommentCreateView(LoginRequiredMixin, CreateView):
#     model = Comment
#     form_class = CommentForm
#
#     def form_valid(self, form):
#         form.instance.author = self.request.user
#         form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])  # Get the associated post
#         return super().form_valid(form)
# @login_required
# def create_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.author = request.user.get_full_name()  # Set the author based on the logged-in user
#             post.postauthor = request.user # Set the ForeignKey to the User object
#             post.save()
#             form.save_m2m()  # If using TaggableManager, save tags after the main post is saved
#             return redirect('post_detail', pk=post.pk)  # Redirect to post detail view
#     else:
#         form = PostForm()
#     return render(request, 'create_post.html', {'form': form})
#
#
# def post_detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     comments = post.comments.all().order_by('-created_at')  # Get comments for the post
#     return render(request, 'post_detail.html', {'post': post, 'comments': comments})
#
#
# @login_required
# @require_POST
# def like_unlike_post(request):
#     post_id = request.POST.get('post_id')
#     action = request.POST.get('action')  # 'like' or 'unlike'
#
#     try:
#         post = Post.objects.get(id=post_id)
#         if action == 'like':
#             post.likes.add(request.user)
#         elif action == 'unlike':
#             post.likes.remove(request.user)
#         return JsonResponse({'success': True, 'likes_count': post.likes.count()})
#     except Post.DoesNotExist:
#         return JsonResponse({'success': False, 'error': 'Post not found.'})
#
#
# @login_required
# def add_comment(request, pk):  # pk is the post's primary key
#     post = get_object_or_404(Post, pk=pk)
#     if request.method == 'POST':
#         form = CommentForm(request.POST)
#         if form.is_valid():
#             comment = form.save(commit=False)
#             comment.post = post
#             comment.author = request.user
#             comment.save()
#             return redirect('post_detail', pk=post.pk)
#     else:
#         form = CommentForm()
#     return render(request, 'add_comment.html', {'form': form, 'post': post})
#
#
# def display_rich_text_tree(tree_data, indent=0):
#     """Displays a rich text tree in a formatted way."""
#
#     node_type = tree_data.get("type")
#
#     if node_type == "doc":
#         for child in tree_data.get("content", []):
#             display_rich_text_tree(child, indent)
#
#     elif node_type == "heading":
#         level = tree_data.get("attrs", {}).get("level", 1)
#         text = "".join(node["text"] for node in tree_data.get("content", []) if node.get("type") == "text")
#         print("#" * level + " " + text)  # Render heading
#
#     elif node_type == "paragraph":
#         text = "".join(process_text_node(node) for node in tree_data.get("content", []) if node.get("type") == "text")
#         print(" " * indent + text)  # Render paragraph
#
#     elif node_type == "reactComponent":
#         print(" " * indent + "[React Component]")  # Placeholder for component
#         for child in tree_data.get("content", []):
#             display_rich_text_tree(child, indent)
#
#     elif node_type == "blockquote":
#         for child in tree_data.get("content", []):
#             display_rich_text_tree(child, indent + 2)  # Indent blockquote
#
#
# def process_text_node(node):
#     """Processes text nodes with marks."""
#     text = node.get("text", "")
#     for mark in node.get("marks", []):
#         if mark.get("type") == "bold":
#             text = f"**{text}**"
#         elif mark.get("type") == "code":
#             text = f"`{text}`"
#         elif mark.get("type") == "strike":
#             text = f"~{text}~"
#     return text
#
# def document_detail(request, pk):
#     document = get_object_or_404(SomePost, pk=pk)
#
#     # Render the tree as text (you'll replace this later with a template)
#     display_rich_text_tree(document.content)
#
#     # Pass the document to a template
#     return render(request, 'document_detail.html', {'document': document})
#
#
# class TodoView(viewsets.ModelViewSet):
#     # create a serializer class and
#     # assign it to the TodoSerializer class
#     serializer_class = CustomUserCreationFormSerializer
#
#     # define a variable and populate it
#     # with the Todo list objects
#     queryset = User.objects.all()


# class RegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = RegisterSerializer
#     permission_classes = (AllowAny,)
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()
#         return Response({
#             "user": UserSerializer(user, context=self.get_serializer_context()).data,
#             "message": "User Created Successfully. Now perform Login to get your token",
#         }, status=status.HTTP_201_CREATED)
#
# class CustomConvertTokenView(ConvertTokenView):
#     pass
#
# class CustomRevokeTokenView(RevokeTokenView):
#     serializer_class = LogoutSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         response = super().post(request, *args, **kwargs)
#         return Response({'detail': 'Successfully logged out.'}, status=response.status_code)
#
#
#
#
# class UserList(generics.ListCreateAPIView):
#     permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
# class UserDetails(generics.RetrieveAPIView):
#     permission_classes = [permissions.IsAuthenticated, TokenHasReadWriteScope]
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
