from django import forms
from .models import Project
from resources.models import Resource
from datetime import date

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        # Exclude auto-calculated and system fields
        fields = [
            'project_name', 'project_type', 'year', 'month', 'resources',
            'assign_project','poc',
            'present_day', 'billable_days', 'non_billable_days', 'is_active'
        ]
        widgets = {
            'project_name': forms.TextInput(attrs={'class': 'form-control'}),
            'project_type': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 2000, 'max': 2100, 'placeholder': 'Year (e.g. 2025)'}),
            'month': forms.Select(attrs={'class': 'form-select'}),
            'resources': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'assign_project': forms.Select(attrs={'class': 'form-select'}),
            'poc': forms.Select(attrs={'class': 'form-select'}),
            'present_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'billable_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'non_billable_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'project_name': 'Project Name',
            'project_type': 'Type',
            'present_day': 'Days Present',
            'billable_days': 'Billable Days',
            'non_billable_days': 'Non-Billable Days',
            'resources': 'Assigned Resources',
            'assign_project': 'Assigned Resource',
            'poc': 'Point of Contact',
            'is_active': 'Active?',
        }
        help_texts = {
            'resources': 'Hold Ctrl (Windows) or Command (Mac) to select multiple resources.',
            'month': 'Month for this project report',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial year/month to current if not provided
        if not self.initial.get('year'):
            self.initial['year'] = date.today().year
        if not self.initial.get('month'):
            self.initial['month'] = date.today().month
        # Only show active resources in dropdowns
        self.fields['resources'].queryset = Resource.active_objects.order_by('resource_name')
        self.fields['assign_project'].queryset = Resource.active_objects.order_by('resource_name')
        self.fields['poc'].queryset = Resource.active_objects.order_by('resource_name')
