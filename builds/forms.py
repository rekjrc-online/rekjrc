from django import forms
from django.forms import inlineformset_factory
from .models import Build, BuildAttribute, BuildAttributeEnum

class BuildForm(forms.ModelForm):
    class Meta:
        model = Build
        fields = [
            'human',
            'profile',
        ]
        widgets = {
            'human': forms.HiddenInput(),
            'profile': forms.HiddenInput(),
        }

class BuildAttributeForm(forms.ModelForm):
    class Meta:
        model = BuildAttribute
        fields = ['attribute_type', 'value']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attribute_type'].queryset = BuildAttributeEnum.objects.order_by('name')

BuildAttributeFormSet = inlineformset_factory(
    Build,
    BuildAttribute,
    form=BuildAttributeForm,
    extra=1,
    can_delete=True
)
