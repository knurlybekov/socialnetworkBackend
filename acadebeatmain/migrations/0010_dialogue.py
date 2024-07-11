# Generated by Django 5.0.6 on 2024-07-11 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acadebeatmain', '0009_delete_dialogue'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dialogue',
            fields=[
                ('dialogueId', models.CharField(default=0, primary_key=True, serialize=False, unique=True)),
                ('data', models.JSONField()),
            ],
        ),
    ]
