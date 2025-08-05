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
    )
    search_fields = ('resource_name',)
    list_filter = ('year', 'month', 'working_days')
    ordering = ['-year', '-month', 'resource_name']
