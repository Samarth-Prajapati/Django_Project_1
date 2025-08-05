from django.contrib import admin
from .models import Project

# Register your models here.

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'project_name',
        'project_type',
        'year',
        'month',
        'billable_days',
        'non_billable_days',
        'billable_hours',
        'non_billable_hours',
        'resource_count',
        'utilization_percentage',
        'is_active',
        'updated_at',
    )
    list_filter = ('project_type', 'year', 'month', 'is_active')
    search_fields = ('project_name',)
    filter_horizontal = ('resources',)  # For ManyToMany field
    readonly_fields = ('billable_hours', 'non_billable_hours', 'created_at', 'updated_at')
    ordering = ['-year', '-month', 'project_name']
