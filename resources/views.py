from django.shortcuts import render, redirect, get_object_or_404
from .models import Resource
from .forms import ResourceForm
from django.contrib import messages
 
 
 
def resource_list(request):
    resources = Resource.active_objects.all()  # Only show active resources
    return render(request, 'resources/resource_list.html', {'resources': resources, 'title': 'Resources'})

def resource_create(request):
    # Get year/month from session (set by dashboard)
    year = request.session.get('selected_year')
    month = request.session.get('selected_month')
    if not (year and month):
        messages.warning(request, 'Please select year and month from dashboard before adding a resource.')
        return redirect('home')
    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.year = year
            resource.month = month
            resource.save()
            messages.success(request, 'Resource created successfully.')
            return redirect('resources:resource_list')
    else:
        form = ResourceForm()
    return render(request, 'resources/resource_form.html', {'form': form, 'title': 'Add Resource', 'year': year, 'month': month})
 
 
def resource_update(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully.')
            return redirect('resources:resource_list')
    else:
        form = ResourceForm(instance=resource)
    return render(request, 'resources/resource_form.html', {'form': form, 'title': 'Edit Resource'})
 
def resource_delete(request, pk):
    resource = get_object_or_404(Resource, pk=pk)
    if request.method == 'POST':
        resource.soft_delete()  # Use soft delete instead of actual deletion
        messages.success(request, 'Resource deleted successfully.')
        return redirect('resources:resource_list')
    return render(request, 'resources/resource_confirm_delete.html', {'resource': resource})
 
 