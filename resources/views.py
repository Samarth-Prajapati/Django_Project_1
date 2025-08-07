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
    """API endpoint that returns optimized resource tree data with all relationships."""
    # Get year and month from session
    selected_year = request.session.get('selected_year')
    selected_month = request.session.get('selected_month')
    
    # Get selected resource ID from request
    selected_resource_id = request.GET.get('resource_id')
    
    # Filter out soft-deleted resources (only active resources) and by session year/month
    resources = Resource.objects.filter(is_active=True)
    
    if selected_year and selected_month:
        resources = resources.filter(year=selected_year, month=selected_month)
    
    # If specific resource selected, filter to that resource only
    if selected_resource_id:
        try:
            resources = resources.filter(id=int(selected_resource_id))
        except (ValueError, TypeError):
            pass  # Invalid resource_id, show all resources
    
    resources = resources.prefetch_related('assigned_projects', 'poc', 'project_assigned_to').all()
    
    # Create comprehensive resource nodes
    resource_trees = []
    
    for resource in resources:
        # Get projects efficiently with single queries
        base_filter = {'is_active': True}
        if selected_year and selected_month:
            base_filter.update({'year': selected_year, 'month': selected_month})
        
        # Get projects where this resource is POC
        poc_projects = Project.objects.filter(poc=resource, **base_filter)
        
        # Get projects where this resource is directly assigned/responsible
        responsible_projects = Project.objects.filter(assign_project=resource, **base_filter)
        
        # Get projects where this resource is assigned (many-to-many)
        assigned_projects = Project.objects.filter(resources=resource, **base_filter)
        
        children = []
        
        # Track counts for summary
        poc_count = poc_projects.count()
        responsible_count = responsible_projects.count()
        assigned_only_count = 0
        
        # Add POC projects
        if poc_count > 0:
            poc_children = []
            for project in poc_projects:
                project_node = {
                    "text": f"{project.project_name}",
                    "icon": "fas fa-bullseye",
                    "type": "project"
                }
                poc_children.append(project_node)
                
            children.append({
                "text": f"POC Projects ({poc_count})",
                "icon": "fas fa-crown",
                "children": poc_children,
                "opened": False,
                "type": "pocProjects"
            })
        
        # Add responsible projects
        if responsible_count > 0:
            resp_children = []
            for project in responsible_projects:
                project_node = {
                    "text": f"{project.project_name}",
                    "icon": "fas fa-clipboard-check",
                    "type": "project"
                }
                resp_children.append(project_node)
                
            children.append({
                "text": f"Responsible Projects ({responsible_count})",
                "icon": "fas fa-user-tie",
                "children": resp_children,
                "opened": False,
                "type": "responsibleProjects"
            })
        
        # Add assigned-only projects (excluding POC and responsible)
        assigned_only = []
        for project in assigned_projects:
            if project.poc != resource and project.assign_project != resource:
                project_node = {
                    "text": f"{project.project_name}",
                    "icon": "fas fa-project-diagram",
                    "type": "project"
                }
                assigned_only.append(project_node)
                assigned_only_count += 1
        
        if assigned_only_count > 0:
            children.append({
                "text": f"Assigned Projects ({assigned_only_count})",
                "icon": "fas fa-tasks",
                "children": assigned_only,
                "opened": False,
                "type": "assignedProjects"
            })
        
        # Calculate total projects
        total_projects = poc_count + responsible_count + assigned_only_count
        
        # Create main resource node
        resource_node = {
            "text": f"{resource.resource_name}",
            "icon": "fas fa-user-circle",
            "opened": True,
            "children": children,
            "type": "resource",
            "resource_data": {
                "id": resource.id,
                "name": resource.resource_name,
                "total_projects": total_projects,
                "poc_count": poc_count,
                "responsible_count": responsible_count,
                "assigned_count": assigned_only_count
            }
        }
        
        resource_trees.append(resource_node)
    
    # Sort resources by total projects (descending) and then by name
    resource_trees.sort(key=lambda x: (-x['resource_data']['total_projects'], x['resource_data']['name']))
    
    return JsonResponse(resource_trees, safe=False)


def resource_list_api(request):
    """API endpoint that returns a list of resources for selection."""
    # Get year and month from session
    selected_year = request.session.get('selected_year')
    selected_month = request.session.get('selected_month')
    
    resources = Resource.objects.filter(is_active=True)
    
    if selected_year and selected_month:
        resources = resources.filter(year=selected_year, month=selected_month)
    
    # Get project counts for each resource
    resource_list = []
    for resource in resources:
        # Count total projects for this resource
        poc_count = Project.objects.filter(poc=resource, is_active=True).count()
        responsible_count = Project.objects.filter(assign_project=resource, is_active=True).count()
        assigned_count = Project.objects.filter(resources=resource, is_active=True).count()
        
        if selected_year and selected_month:
            poc_count = Project.objects.filter(
                poc=resource, is_active=True, year=selected_year, month=selected_month
            ).count()
            responsible_count = Project.objects.filter(
                assign_project=resource, is_active=True, year=selected_year, month=selected_month
            ).count()
            assigned_count = Project.objects.filter(
                resources=resource, is_active=True, year=selected_year, month=selected_month
            ).count()
        
        total_projects = poc_count + responsible_count + assigned_count
        
        resource_list.append({
            'id': resource.id,
            'name': resource.resource_name,
            'total_projects': total_projects,
            'poc_count': poc_count,
            'responsible_count': responsible_count,
            'assigned_count': assigned_count
        })
    
    # Sort by total projects (descending) and then by name
    resource_list.sort(key=lambda x: (-x['total_projects'], x['name']))
    
    return JsonResponse(resource_list, safe=False)
