# Generated by Django 5.0.6 on 2024-07-10 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acadebeatmain', '0004_rename_dialogjson_dialogjsonmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='DialogueMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('image_path', models.CharField(max_length=255)),
                ('message_id', models.CharField(max_length=50)),
                ('content', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Dialogue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dialogue_id', models.CharField(max_length=50)),
                ('messages', models.ManyToManyField(to='acadebeatmain.dialoguemessage')),
            ],
        ),
    ]
