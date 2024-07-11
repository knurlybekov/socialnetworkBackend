import json


from django.db import models
from django.db.models.fields.json import JSONField
from django.http import JsonResponse
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
from django.views import View
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer

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
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    password = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    username = models.CharField(max_length=255, blank=True)
    image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_online = models.DateTimeField(auto_now=True)
    date_of_birth = models.DateField(null=True, blank=True)
    rating = models.IntegerField(default=0)
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
    author = models.CharField(max_length=100)
    postauthor = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=now, blank=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager(blank=True)
    category = models.CharField(max_length=200)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)  # Use your User model


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # Use your User model
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)  # Use your User model


class UserFollowing(models.Model):
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE)
    following_user_id = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="followers", on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_id', 'following_user_id')  # Use the correct field names


class SomePost(models.Model):
    title = models.CharField(max_length=200)  # Optional title for the document
    content = models.JSONField(encoder=DjangoJSONEncoder)


# class dialogjsonmodel(models.Model):
#     data = models.JSONField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     def __str__(self):
#         return str(self.id)


# class DialogueMessage(models.Model):
#     name = models.CharField(max_length=100)
#     image_path = models.CharField(max_length=255)
#     message_id = models.CharField(max_length=50)  # Adjust length as needed
#     content = models.TextField()

class Dialogue(models.Model):
    dialogueId = models.CharField(primary_key=True, unique=True, default=0 )
    data = models.JSONField()  # Store the entire JSON





# class DialogueExample(models.Model):
#     dialogue_id = models.BigAutoField(primary_key=True, editable=False)
#     name = models.CharField(max_length=100)
#     detail_text = models.TextField()
#     detail_json = JSONField()  # requires Django-Mysql package
#
    # def detail_json_formatted(self):
    #     # dump the json with indentation set
    #
    #     # example for detail_text TextField
    #     # json_obj = json.loads(self.detail_text)
    #     # data = json.dumps(json_obj, indent=2)
    #
    #     # with JSON field, no need to do .loads
    #     data = json.dumps(self.detail_json, indent=2)
    #
    #     # format it with pygments and highlight it
    #     formatter = HtmlFormatter(style='colorful')
    #     response = highlight(data, JsonLexer(), formatter)
    #
    #     # include the style sheet
    #     style = "<style>" + formatter.get_style_defs() + "</style><br/>"
    #
    #     return mark_safe(style + response)
    #
    # detail_json_formatted.short_description = 'Details Formatted'
#
#     class Meta:
#         managed = True
#         db_table = 'dialogue_example'
#         verbose_name = 'Dialogue Example'
#         verbose_name_plural = 'Dialogues Examples'
