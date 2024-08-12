from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from acadebeatmain.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create profiles for all users without a profile'

    def handle(self, *args, **kwargs):
        users_without_profiles = User.objects.filter(profile__isnull=True)
        for user in users_without_profiles:
            Profile.objects.get_or_create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Profile created for user {user.username}'))