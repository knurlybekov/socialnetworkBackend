from . import views
from django.contrib.auth.views import LoginView
from django.contrib.auth.views import LogoutView
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
                  path('admin/', admin.site.urls),
    re_path('login', views.login),
re_path('signup', views.signup),
re_path('test_token', views.test_token),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)