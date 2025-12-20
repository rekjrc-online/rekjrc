from django import forms
from .models import Profile

RACE_TYPE_CHOICES = [
    ('Lap Race',        'Lap Race'),
    ('Drag Race',       'Drag Race'),
    ('Crawler Comp',    'Crawler Comp'),
    ('Stopwatch Race',  'Stopwatch Race'),
    ('Long Jump',       'Long Jump'),
    ('Top Speed',       'Top Speed'),
    ('Judged Event',    'Judged Event')
]

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
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = self.instance
        if profile.profiletype == "race":
            print("hi")
            self.fields['race_type'] = forms.ChoiceField(
                choices=RACE_TYPE_CHOICES,
                required=True,
                label="Race Type",
                widget=forms.Select(attrs={'class': 'full-width'})
            )

class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['displayname', 'bio', 'avatar', 'city', 'state', 'website']
        widgets = {
            'displayname': forms.TextInput(attrs={'class': 'full-width'}),
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'full-width'}),
            'avatar': forms.ClearableFileInput(attrs={
                'class': 'full-width',
                'accept': 'image/*'
            }),
            'city': forms.TextInput(attrs={'class': 'full-width'}),
            'state': forms.TextInput(attrs={'class': 'full-width'}),
            'website': forms.URLInput(attrs={'class': 'full-width'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        profile = self.instance
        special_types = ['CLUB', 'TEAM', 'STORE', 'LOCATION']
        if profile.profiletype in special_types:
            self.fields['chat_enabled'] = forms.BooleanField(
                required=False,
                label="Enable Chat room",
                widget=forms.CheckboxInput(attrs={'class': 'full-width'})
            )
