from django import forms
from .models import Resource as ResourceModel

class ResourceForm(forms.ModelForm):
    class Meta:
        model = ResourceModel
        fields = ['resource_name', 'working_days', 'present_day', 'present_hours']
        widgets = {
            'resource_name': forms.TextInput(attrs={'class': 'form-control'}),
            'working_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'placeholder': 'Leave blank for auto-calculation'
            }),
            'present_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'present_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'})
        }
        labels = {
            'resource_name': 'Resource Name',
            'present_day': 'Days Present',
            'present_hours': 'Hours Present',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text for working days
        self.fields['working_days'].required = False
        if self.instance and self.instance.pk:
            self.fields['working_days'].help_text = f"Auto-calculated value: {getattr(self.instance, 'get_working_days_for_display', lambda: '')()}"
        else:
            self.fields['working_days'].help_text = "Auto-calculated if left blank."

    def clean(self):
        cleaned_data = super().clean()
        resource_name = cleaned_data.get('resource_name')
        # year and month are set in the view, so get from instance or session
        year = getattr(self.instance, 'year', None)
        month = getattr(self.instance, 'month', None)
        if resource_name and year and month:
            from .models import Resource as ResourceModel
            qs = ResourceModel.objects.filter(resource_name=resource_name, year=year, month=month)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                from django.core.exceptions import ValidationError
                raise ValidationError("A resource with this name, year, and month already exists.")
        return cleaned_data