from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin
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
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
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