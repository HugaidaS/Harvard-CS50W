# Generated by Django 4.2.11 on 2024-06-19 13:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MyDoctorApp', '0013_blacklist_appointment_note_appointment_status_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='availability',
            name='appointment',
        ),
    ]
