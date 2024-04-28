from django.contrib import admin

# Register your models here.
from .models import User, Appointment, Document

admin.site.register(User)
admin.site.register(Appointment)
admin.site.register(Document)
