from django.db import models
from django.db.models import ImageField
from django.utils import timezone
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # doctor or patient role
    role = models.CharField(max_length=10)
    photo = ImageField(upload_to='user_photos/', default='media/default.png')
    saved_users = models.ManyToManyField('self', symmetrical=False, related_name='saved_by')


class Availability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    appointment_date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_reserved = models.BooleanField(default=False)
    appointment = models.OneToOneField(
        'Appointment',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='related_availability'
    )


class Appointment(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    availability = models.ForeignKey(Availability, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')


class Document(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)