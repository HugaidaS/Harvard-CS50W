from django import forms
from django.utils import timezone
from .models import Availability, User


class ProfileImageForm(forms.ModelForm):
    photo = forms.ImageField(label='', help_text='', widget=forms.FileInput)
    class Meta:
        model = User
        fields = ['photo']


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['appointment_date', 'start_time', 'end_time']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'min': timezone.localdate()}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super(AvailabilityForm, self).__init__(*args, **kwargs)
        # Set the default date for the current day
        self.fields['appointment_date'].initial = timezone.localdate()