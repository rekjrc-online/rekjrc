# drivers/forms.py
from django import forms
from profiles.models import Profile

class DriverProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['displayname', 'avatar', 'bio', 'city', 'state', 'website']
