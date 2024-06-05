# # accounts/forms.py
# from django.contrib.auth.forms import UserCreationForm, UserChangeForm
#
# from .models import CustomUser
#
#
# class CustomUserCreationForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ("username", "email")
#
#
# class CustomUserChangeForm(UserChangeForm):
#     class Meta:
#         model = CustomUser
#         fields = ("username", "email")
# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from taggit.forms import TagField, TagWidget
from acadebeatmain.models import Post, Comment


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2']  # Add other fields you want to include in your form


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'first_name', 'last_name', 'password', 'username', 'image', 'date_of_birth']  # Add other fields you wish to be editable


class PostForm(forms.ModelForm):
    tags = forms.CharField(
        label='Tags (comma-separated)',
        widget=TagWidget(),
        required=False,
    )
    category = forms.CharField()

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'tags']  # Include 'tags' in the fields


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']