# Generated by Django 5.0.6 on 2024-06-28 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acadebeatmain', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='auth_provider',
            field=models.CharField(default='email', max_length=255),
        ),
        migrations.AddField(
            model_name='user',
            name='is_teacher',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
