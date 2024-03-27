from django import forms
from .models import User, Category, Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ['author']  # Exclude the author field from the form

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)  # Retrieve the author from kwargs
        super(ListingForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        instance = super(ListingForm, self).save(commit=False)
        if self.author:
            instance.author = self.author  # Assign the author
        if commit:
            instance.save()
        return instance
