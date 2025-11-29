from django import forms
from django.forms import inlineformset_factory
from .models import Club, ClubMember, ClubLocation

class ClubForm(forms.ModelForm):
    class Meta:
        model = Club
        fields = ['human', 'profile']
        widgets = {
            'human': forms.HiddenInput(),
            'profile': forms.HiddenInput(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['human'].required = False
        self.fields['profile'].required = False

class ClubMemberForm(forms.ModelForm):
    class Meta:
        model = ClubMember
        fields = ['human', 'role']

class ClubLocationForm(forms.ModelForm):
    class Meta:
        model = ClubLocation
        fields = ['location']
        widgets = {
            'location': forms.Select(attrs={'class': 'styled-dropdown'})
        }

# Formsets
ClubMemberFormSet = inlineformset_factory(
    Club, ClubMember, form=ClubMemberForm, extra=1, can_delete=True
)
ClubLocationFormSet = inlineformset_factory(
    Club, ClubLocation, form=ClubLocationForm, extra=1, can_delete=True
)
