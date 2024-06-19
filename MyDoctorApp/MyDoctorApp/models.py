from django.db import models
from django.db.models import ImageField
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from datetime import timedelta


class User(AbstractUser):
    # doctor or patient role
    role = models.CharField(max_length=10)
    photo = ImageField(upload_to='user_photos/', default='media/default.png')
    saved_users = models.ManyToManyField('self', symmetrical=False, related_name='saved_by')
    missed_appointments = models.IntegerField(default=0)


class Availability(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE)
    appointment_date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_reserved = models.BooleanField(default=False)


class Appointment(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor')
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='patient')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    availability = models.ForeignKey(Availability, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    STATUS_CHOICES = [
        ('Booked', 'Booked'),
        ('Canceled', 'Canceled'),
        ('Happened', 'Happened'),
        ('Patient Absent', 'Patient Absent'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Booked')
    note = models.TextField(null=True, blank=True)


class Blacklist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_added = models.DateField(default=timezone.now)

    @property
    def is_active(self):
        return (timezone.now() - self.date_added) <= timedelta(days=30)