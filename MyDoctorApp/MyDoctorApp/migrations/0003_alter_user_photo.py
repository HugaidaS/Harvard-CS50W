# Generated by Django 4.2.11 on 2024-05-01 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyDoctorApp', '0002_user_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(default='media/user_photos/default.png', upload_to='user_photos/'),
        ),
    ]
