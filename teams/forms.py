from django import forms
from django.forms import inlineformset_factory
from .models import Team, TeamMember

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = [
            'human',
            'profile'
        ]
        widgets = {
            'human': forms.HiddenInput(),
            'profile': forms.HiddenInput(),
        }

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = ['human', 'role']

TeamMemberFormSet = inlineformset_factory(
    Team,
    TeamMember,
    form=TeamMemberForm,
    extra=1,
    can_delete=True
)