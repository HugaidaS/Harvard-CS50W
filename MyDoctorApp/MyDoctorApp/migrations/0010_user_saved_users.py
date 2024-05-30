# Generated by Django 4.2.11 on 2024-05-30 16:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyDoctorApp', '0009_chat_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='saved_users',
            field=models.ManyToManyField(related_name='saved_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
