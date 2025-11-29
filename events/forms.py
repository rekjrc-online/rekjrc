from django import forms
from .models import Event, EventInterest

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['location', 'eventdate']
        widgets = {
            'location': forms.Select(attrs={'class': 'styled-dropdown'}),
            'eventdate': forms.DateInput(attrs={'type': 'date', 'class': 'styled-date'}, format='%Y-%m-%d'),
        }

class EventInterestForm(forms.ModelForm):
    class Meta:
        model = EventInterest
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional note...'}),
        }
