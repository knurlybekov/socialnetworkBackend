import json

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.fields.json import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.views import View
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
# from pygments.lexers.data import JsonLexer

from taggit.managers import TaggableManager
from acadebeat import settings
from django.core.serializers.json import DjangoJSONEncoder


class CustomUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("You have not provided an email")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)
        return self._create_user(email, password, **extra_fields)


AUTH_PROVIDERS = {"facebook": "facebook", "twitter": "twitter", "instagram": "instagram", "google": "google",
                  "email": "email"}


class User(AbstractBaseUser, PermissionsMixin):
    def user_directory_path(instance, filename):
        # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
        return f'{instance.email}/profiles/{filename}'

    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_online = models.DateTimeField(auto_now=True)
    date_of_birth = models.DateField(null=True, blank=True)
    rating = models.IntegerField(default=0)
    # following_id = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followers', blank=True)
    # subscriptions = models.ManyToManyField('self', through='UserSubscription', symmetrical=False,
    #                                        related_name='subscribers', through_fields=('subscriber', 'subscribed_to'))
    posts = models.IntegerField(default=0)
    is_teacher = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    auth_provider = models.CharField(max_length=255, blank=False, null=False, default=AUTH_PROVIDERS.get('email'))
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    access_token = models.CharField(max_length=255, blank=True)
    refresh_token = models.CharField(max_length=255, blank=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']


    # def __str__(self):
    #     return self.username
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Post(models.Model):
    # author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')  # Use your User model
    # author = models.CharField(max_length=100)
    postauthor = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(blank=True)
    category = models.CharField(max_length=200)

    def like(self, user):
        """Likes the post on behalf of the given user."""
        content_type = ContentType.objects.get_for_model(Post)
        Like.objects.get_or_create(
            user=user, content_type=content_type, object_id=self.id
        )

    def unlike(self, user):
        """Unlikes the post on behalf of the given user."""
        content_type = ContentType.objects.get_for_model(Post)
        Like.objects.filter(
            user=user, content_type=content_type, object_id=self.id
        ).delete()

    def is_liked_by(self, user):
        """Checks if the post is liked by the given user."""
        content_type = ContentType.objects.get_for_model(Post)
        return Like.objects.filter(
            user=user, content_type=content_type, object_id=self.id
        ).exists()
    # likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)  # Use your User model


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Use your User model
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def like(self, user):
        """Likes the comment on behalf of the given user."""
        content_type = ContentType.objects.get_for_model(Comment)
        Like.objects.get_or_create(
            user=user, content_type=content_type, object_id=self.id
        )

    def unlike(self, user):
        """Unlikes the comment on behalf of the given user."""
        content_type = ContentType.objects.get_for_model(Comment)
        Like.objects.filter(
            user=user, content_type=content_type, object_id=self.id
        ).delete()

    def is_liked_by(self, user):
        """Checks if the comment is liked by the given user."""
        content_type = ContentType.objects.get_for_model(Comment)
        return Like.objects.filter(
            user=user, content_type=content_type, object_id=self.id
        ).exists()
    # likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)  # Use your User model


# class UserFollowing(models.Model):
#     user_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE)
#     following_user_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="followers", on_delete=models.CASCADE)
#     created = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         unique_together = ('user_id', 'following_user_id')  # Use the correct field names


# class SomePost(models.Model):
#     title = models.CharField(max_length=200)  # Optional title for the document
#     content = models.JSONField(encoder=DjangoJSONEncoder)


class Dialogue(models.Model):
    dialogueId = models.CharField(primary_key=True, unique=True, default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=2)
    data = models.JSONField()  # Store the entire JSON


class Subscription(models.Model):
    subscriber = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')

    subscribed_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subscriber', 'subscribed_to')
    # class Profile(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     following = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='followers', blank=True)
#
#
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance)
#
#
# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()

# content types (8 - post, 9 - comment)
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Generic Foreign Key to handle likes on both Posts and Comments
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')