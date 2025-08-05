from django.contrib import admin
from .models import Resource

# Register your models here.

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        'resource_name',
        'year',
        'month',
        'working_days',
        'present_day',
        'present_hours',
        'is_active',  # Show active status
    )
    search_fields = ('resource_name',)
    list_filter = ('year', 'month', 'working_days', 'is_active')  # Add is_active filter
    ordering = ['-year', '-month', 'resource_name']
