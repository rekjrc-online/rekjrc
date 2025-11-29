from django import forms
from .models import Store

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = [
            'profile',
            'human'
        ]
        widgets = {
            'human': forms.HiddenInput(),
            'profile': forms.HiddenInput(),
        }
