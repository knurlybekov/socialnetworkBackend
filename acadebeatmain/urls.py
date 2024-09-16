from rest_framework.routers import DefaultRouter

from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from .views import EditProfileView, PostCreateView, PostDetailView, CommentCreateView, \
    DialogueCreateAPIView, DialogueRetrieveAPIView, DialogueListAPIView, \
    GetUserProfileAPIView, LoginView, LogoutView, UserSearchView, AllPostsByUserId, PostListView, LikeUnlikePostView, \
    ListSubscriptionsAPIView, CreateSubscriptionAPIView, DeleteSubscriptionAPIView, CreateLikeAPIView, \
    DeleteLikeAPIView, PostLikesAPIView

# router = DefaultRouter()
# router.register(r'dialogues/<int:pk>/', DialogueRetrieveAPIView.as_view(), base_name='dialogue_detail')
# router.register(r'dialogues/<int:pk>/', DialogueRetrieveAPIView.as_view(), base_name='dialogue_download')
#
# urlpatterns = router.urls


urlpatterns = [
                  path('admin/', admin.site.urls),
                  re_path(r'^auth/', include('drf_social_oauth2.urls', namespace='drf')),
                  path('health/', views.health),
                  path('login', LoginView.as_view(), name='login'),
                  path('logout', LogoutView.as_view(), name='logout'),
                  path('dialogues/<int:pk>/', DialogueRetrieveAPIView.as_view({'get': 'retrieve'}),
                       name='dialogue-detail'),
                  path('dialogues/create/', DialogueCreateAPIView.as_view()),
                  path('dialogues/', DialogueListAPIView.as_view(), name='dialogue-list'),  # Added line
                  path('signup', views.signup),
                  path('myprofile', GetUserProfileAPIView.as_view(), name='my-profile'),
                  re_path('test_token', views.test_token),
                  path('profile/edit', EditProfileView.as_view(), name='edit_profile'),
                  path('users/search', UserSearchView.as_view(), name='user_search'),
                  # re_path(r'^follow/$', follow, name='follow'),
                  # re_path(r'^unfollow/$', unfollow, name='unfollow'),
                  path('posts/create/', PostCreateView.as_view(), name='create_post'),
                  path('posts/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
                  path('posts/createdby/<int:pk>/', AllPostsByUserId.as_view(), name='all_posts_createdby'),
                  path('posts/all', PostListView.as_view(), name='all_posts'),
                  # path('posts/<int:pk>/like/', LikeUnlikePostView.as_view(), name='like_unlike_post'),
                  path('posts/<int:pk>/comment/', CommentCreateView.as_view(), name='comment_post'),
                  path('posts/<int:post_id>/likes', PostLikesAPIView.as_view(), name='likes'),
                  path('subscriptions/', ListSubscriptionsAPIView.as_view(), name='subscription-list'),
                  path('subscriptions/<int:pk>/', CreateSubscriptionAPIView.as_view(), name='subscription-create'),
                  path('subscriptions/<int:pk>/delete/', DeleteSubscriptionAPIView.as_view(),
                       name='subscription-delete'),
                  # re_path(r'^posts/(?P<post_id>\d+)/comments/create/$', CommentCreateView.as_view(),
                  #         name='create_comment'),
                  path('<int:object_id>/like/', CreateLikeAPIView.as_view(), name='like-create'),
                  path('<int:object_id>/unlike/', DeleteLikeAPIView.as_view(), name='like-delete'),
                  path('dialogues/<int:pk>/download/', DialogueRetrieveAPIView.as_view({'get': 'download'})),
                  # re_path(r'^posts/like/$', like_unlike_post, name='like_unlike_post'),
                  # re_path(r'^posts/(?P<pk>\d+)/comments/add/$', add_comment, name='add_comment'),

              ] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
