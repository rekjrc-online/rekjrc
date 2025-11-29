from django import forms
from .models import Profile

class ProfileCreateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profiletype', 'displayname', 'bio', 'avatar', 'city', 'state', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'full-width'}),
            'displayname': forms.TextInput(attrs={'class': 'full-width'}),
            'city': forms.TextInput(attrs={'class': 'full-width'}),
            'state': forms.TextInput(attrs={'class': 'full-width'}),
            'website': forms.URLInput(attrs={'class': 'full-width'}),
        }

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        # exclude profiletype from the edit form
        fields = ['displayname', 'bio', 'avatar', 'city', 'state', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'full-width'}),
            'displayname': forms.TextInput(attrs={'class': 'full-width'}),
            'city': forms.TextInput(attrs={'class': 'full-width'}),
            'state': forms.TextInput(attrs={'class': 'full-width'}),
            'website': forms.URLInput(attrs={'class': 'full-width'}),
        }

