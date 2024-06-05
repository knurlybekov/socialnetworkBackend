from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from .views import signup, user_profile, edit_profile, create_post

urlpatterns = [
    path("", views.home, name="home"),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('user/<int:user_id>/', user_profile, name='user_profile'),
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('search_results/', views.search_results, name='search_results'),
    path('follow/', views.follow, name='follow'),
    path('unfollow/', views.unfollow, name='unfollow'),
    path('create_post/', create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('like_unlike_post/', views.like_unlike_post, name='like_unlike_post'),
    path('post/<int:pk>/add_comment/', views.add_comment, name='add_comment'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)