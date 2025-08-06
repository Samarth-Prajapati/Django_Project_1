from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Resource
from .forms import ResourceForm
from django.contrib import messages
from projects.models import Project
 
 
 
def resource_list(request):
    # Get year and month from session (set by home page)
    selected_year = request.session.get('selected_year')
    selected_month = request.session.get('selected_month')
    
    # If no session values, redirect to home page to set them
    if not selected_year or not selected_month:
        return redirect('dashboard_home')
    
    resources = Resource.active_objects.all()  # Only show active resources
    resources = resources.filter(year=selected_year, month=selected_month)
    
    return render(request, 'resources/resource_list.html', {
        'resources': resources,
        'title': 'Resources',
        'selected_year': selected_year,
        'selected_month': selected_month,
    })

def resource_create(request):
    # Get year/month from session (set by dashboard)
    year = request.session.get('selected_year')
    month = request.session.get('selected_month')
    
    if not (year and month):
        messages.warning(request, 'Please select year and month from dashboard before adding a resource.')
        return redirect('dashboard_home')
        
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


def resource_canvas_tree_visualization(request):
    """Render the interactive Canvas-based resource tree visualization page."""
    return render(request, 'resources/resource_canvas_tree.html')


def resource_tree_view(request):
    """API endpoint that returns resource tree data as JSON with individual resource nodes."""
    # Get year and month from session
    selected_year = request.session.get('selected_year')
    selected_month = request.session.get('selected_month')
    
    # Filter out soft-deleted resources (only active resources) and by session year/month
    resources = Resource.objects.filter(is_active=True)
    
    if selected_year and selected_month:
        resources = resources.filter(year=selected_year, month=selected_month)
    
    resources = resources.all()
    
    # Create resource nodes - each resource as a separate tree
    resource_trees = []
    for resource in resources:
        # Get projects where this resource is assigned (many-to-many)
        assigned_projects = Project.objects.filter(
            resources=resource, 
            is_active=True
        )
        if selected_year and selected_month:
            assigned_projects = assigned_projects.filter(year=selected_year, month=selected_month)
        
        # Get projects where this resource is POC
        poc_projects = Project.objects.filter(
            poc=resource, 
            is_active=True
        )
        if selected_year and selected_month:
            poc_projects = poc_projects.filter(year=selected_year, month=selected_month)
        
        # Get projects where this resource is assigned as single resource
        single_assigned_projects = Project.objects.filter(
            assign_project=resource, 
            is_active=True
        )
        if selected_year and selected_month:
            single_assigned_projects = single_assigned_projects.filter(year=selected_year, month=selected_month)
        
        # Create children nodes for projects
        children = []
        
        # Add assigned projects (many-to-many relationship)
        if assigned_projects.exists():
            children.append({
                "text": "👥 Assigned Projects",
                "icon": "fas fa-tasks",
                "children": [
                    {
                        "text": f"{project.project_name}",
                        "icon": "fas fa-project-diagram"
                    } for project in assigned_projects
                ],
                "opened": True
            })
        
        # Add POC projects
        if poc_projects.exists():
            children.append({
                "text": "🎯 POC Projects",
                "icon": "fas fa-bullseye",
                "children": [
                    {
                        "text": f"{project.project_name}",
                        "icon": "fas fa-project-diagram"
                    } for project in poc_projects
                ],
                "opened": True
            })
        
        # Add single assigned projects
        if single_assigned_projects.exists():
            children.append({
                "text": "📋 Directly Assigned Projects",
                "icon": "fas fa-user-tie",
                "children": [
                    {
                        "text": f"{project.project_name}",
                        "icon": "fas fa-project-diagram"
                    } for project in single_assigned_projects
                ],
                "opened": True
            })
        
        # Create resource node
        resource_node = {
            "text": f"{resource.resource_name}",
            "icon": "fas fa-user",
            "opened": True,
            "children": children
        }
        
        resource_trees.append(resource_node)
    
    return JsonResponse(resource_trees, safe=False)


def resource_list_api(request):
    """API endpoint that returns a list of resources for selection."""
    # Get year and month from session
    selected_year = request.session.get('selected_year')
    selected_month = request.session.get('selected_month')
    
    resources = Resource.objects.filter(is_active=True)
    
    if selected_year and selected_month:
        resources = resources.filter(year=selected_year, month=selected_month)
    
    resources = resources.values('id', 'resource_name', 'present_day', 'present_hours')
    resource_list = [
        {
            'id': r['id'],
            'name': r['resource_name'],
            'present_day': r['present_day'],
            'present_hours': r['present_hours']
        }
        for r in resources
    ]
    return JsonResponse(resource_list, safe=False)