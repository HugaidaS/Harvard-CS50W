# Generated by Django 4.2.11 on 2024-05-01 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyDoctorApp', '0003_alter_user_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='photo',
            field=models.ImageField(default='default.png', upload_to='user_photos/'),
        ),
    ]
