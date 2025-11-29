from django import forms
from .models import Location

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = [
            'human',
            'profile',
            'latitude',
            'longitude',
        ]
        widgets = {
            'human': forms.HiddenInput(),
            'profile': forms.HiddenInput(),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
        }
