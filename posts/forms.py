from django import forms
from profiles.models import Profile
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['profile', 'content', 'image', 'video_url']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': "What's happening?",
                'class': 'full-width'
            }),
            'profile': forms.Select(attrs={'class': 'full-width'}),
            'image': forms.ClearableFileInput(attrs={'class': 'full-width'}),
            'video_url': forms.URLInput(attrs={'class': 'full-width'}),
        }

    def __init__(self, *args, **kwargs):
        self.human = kwargs.pop('human', None)
        super().__init__(*args, **kwargs)
        if self.human:
            self.fields['profile'].queryset = Profile.objects.filter(human=self.human).order_by('profiletype', 'displayname')
        self.fields['profile'].label_from_instance = lambda obj: f"{obj.get_profiletype_display()} - {obj.displayname}"

    def clean_profile(self):
        profile = self.cleaned_data.get('profile')
        if profile and profile.human != self.human:
            raise forms.ValidationError("Invalid profile selected.")
        return profile