from django.contrib import admin

# Register your models here.
from .models import User, Appointment, Blacklist, Availability

admin.site.register(User)
admin.site.register(Appointment)
admin.site.register(Blacklist)
admin.site.register(Availability)
