from django import forms
from django.forms import inlineformset_factory
from .models import Race, RaceAttribute, Track

class LapMonitorUploadForm(forms.Form):
    race = forms.IntegerField(widget=forms.HiddenInput())
    csv_file = forms.FileField(label="LapMonitor CSV File")

class RaceForm(forms.ModelForm):
    class Meta:
        model = Race
        fields = [
            "race_type",
            "event",
            "location",
            "track",
            "club",
            "team",
            "transponder",
        ]
        widgets = {
            field: forms.Select(attrs={"class": "form-control"})
            for field in fields
        }

class RaceAttributeForm(forms.ModelForm):
    class Meta:
        model = RaceAttribute
        fields = ("attribute", "value")
        widgets = {
            "attribute": forms.TextInput(attrs={"class": "form-control", "placeholder": "Attribute name"}),
            "value": forms.TextInput(attrs={"class": "form-control", "placeholder": "Value"}),
        }

RaceAttributeFormSet = inlineformset_factory(
    Race,
    RaceAttribute,
    form=RaceAttributeForm,  # explicitly use the custom form above
    fields=("attribute", "value"),
    extra=1,
    can_delete=True,
)