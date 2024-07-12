from rest_framework.routers import DefaultRouter

from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from .views import EditProfileView, search_results, follow, unfollow, PostCreateView, PostDetailView, CommentCreateView, \
    like_unlike_post, add_comment, DialogueCreateAPIView

# router = DefaultRouter()

urlpatterns = [
                  path('admin/', admin.site.urls),
                  re_path('health/', views.health),
                  re_path('login', views.login),
                  path('dialogues/', DialogueCreateAPIView.as_view()),
                  re_path('signup', views.signup),
                  re_path('test_token', views.test_token),
                  re_path('profile/edit', EditProfileView.as_view(), name='edit_profile'),
                  re_path(r'^profile/edit/$', EditProfileView.as_view(), name='edit_profile'),
                  re_path(r'^search/$', search_results, name='search_results'),
                  re_path(r'^follow/$', follow, name='follow'),
                  re_path(r'^unfollow/$', unfollow, name='unfollow'),
                  re_path(r'^posts/create/$', PostCreateView.as_view(), name='create_post'),
                  re_path(r'^posts/(?P<pk>\d+)/$', PostDetailView.as_view(), name='post_detail'),
                  re_path(r'^posts/(?P<post_id>\d+)/comments/create/$', CommentCreateView.as_view(),
                          name='create_comment'),
                  re_path(r'^posts/like/$', like_unlike_post, name='like_unlike_post'),
                  re_path(r'^posts/(?P<pk>\d+)/comments/add/$', add_comment, name='add_comment'),
                  re_path(r'^auth/', include('drf_social_oauth2.urls', namespace='drf')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
