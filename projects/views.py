from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from .models import Project
from .forms import ProjectForm
from resources.models import Resource
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
import base64


def team_dashboard_redirect(request):
    return redirect('dashboard_home')


def dashboard_home(request):
    years = list(range(2020, 2031))
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    # Get year and month from GET params, fallback to current year/month
    now = datetime.now()
    year_param = request.GET.get('year')
    month_param = request.GET.get('month')
    try:
        year = int(year_param) if year_param else now.year
    except ValueError:
        year = now.year
    try:
        month = int(month_param) if month_param else now.month
    except ValueError:
        month = now.month
    
    # Always store the selected year and month in session (either from params or current)
    request.session['selected_year'] = year
    request.session['selected_month'] = month
    # Filter projects/resources by year and month (month as number)
    from resources.models import Resource
    from .models import Project
    projects = Project.active_objects.filter(year=year, month=month)  # Only active projects
    resources = Resource.active_objects.filter(year=year, month=month)  # Only active resources
    return render(request, 'home.html', {
        'years': years,
        'months': months,
        'year': year,
        'month': month,
        'projects': projects,
        'resources': resources,
        'current_year': now.year,
        'current_month': now.month,
    })

def project_list(request):
    # Get year and month from session (set by home page)
    selected_year = request.session.get('selected_year')
    selected_month = request.session.get('selected_month')
    
    # If no session values, redirect to home page to set them
    if not selected_year or not selected_month:
        return redirect('dashboard_home')
    
    projects = Project.active_objects.all()  # Only show active projects
    projects = projects.filter(year=selected_year, month=selected_month)
    
    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'selected_year': selected_year,
        'selected_month': selected_month,
    })


def project_create(request):
    year = request.session.get('selected_year')
    month = request.session.get('selected_month')
    
    # If no session values, redirect to home page to set them
    if not year or not month:
        return redirect('dashboard_home')
        
    if request.method == 'POST':
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            project = project_form.save(commit=False)
            project.year = year
            project.month = month
            project.save()
            return redirect('projects:project_list')
    else:
        project_form = ProjectForm(initial={'year': year, 'month': month})

    return render(request, 'projects/project_form.html', {
        'form': project_form,
        'title': 'Create Project',
        'year': year,
        'month': month
    })


def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project_form = ProjectForm(request.POST, instance=project)
        if project_form.is_valid():
            project_form.save()
            return redirect('projects:project_list')
    else:
        project_form = ProjectForm(instance=project)

    return render(request, 'projects/project_form.html', {
        'form': project_form,
        'title': 'Edit Project'
    })


def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.soft_delete()  # Use soft delete instead of actual deletion
        return redirect('projects:project_list')
    return render(request, 'projects/project_confirm_delete.html', {'project':project})


def project_tree_visualization(request):
    """Render the project tree visualization page."""
    return render(request, 'projects/project_tree.html')

def project_canvas_tree_visualization(request):
    """Render the interactive Canvas-based project tree visualization page."""
    return render(request, 'projects/project_canvas_tree.html')


def project_tree_html(request):
    """Generate an HTML-based tree visualization that doesn't require external dependencies."""
    try:
        # Get year and month from session
        selected_year = request.session.get('selected_year')
        selected_month = request.session.get('selected_month')
        
        projects = Project.objects.prefetch_related('resources', 'assign_project', 'poc')
        
        if selected_year and selected_month:
            projects = projects.filter(year=selected_year, month=selected_month)
        
        projects = projects.all()
        
        # Create HTML tree structure
        html_tree = ['<div class="tree-container">']
        html_tree.append('<h3>Project Tree Structure</h3>')
        html_tree.append('<ul class="tree">')
        html_tree.append('<li><strong>Projects</strong>')
        html_tree.append('<ul>')
        
        for project in projects:
            html_tree.append(f'<li><strong>{project.project_name}</strong> ({project.get_project_type_display()})')
            html_tree.append('<ul>')
            
            # Add assigned resource
            if project.assign_project:
                html_tree.append(f'<li>📋 Assigned Resource: {project.assign_project.resource_name}</li>')
            
            # Add resources
            resources = project.resources.all()
            if resources:
                html_tree.append(f'<li>👥 Resources ({len(resources)})')
                html_tree.append('<ul>')
                for res in resources:
                    html_tree.append(f'<li>👤 {res.resource_name}</li>')
                html_tree.append('</ul>')
                html_tree.append('</li>')
            
            # Add POC
            if project.poc:
                html_tree.append(f'<li>🎯 POC: {project.poc.resource_name}</li>')
            
            html_tree.append('</ul>')
            html_tree.append('</li>')
        
        html_tree.append('</ul>')
        html_tree.append('</li>')
        html_tree.append('</ul>')
        html_tree.append('</div>')
        
        # Add CSS styling
        css = """
        <style>
        .tree-container { font-family: Arial, sans-serif; padding: 20px; }
        .tree, .tree ul { list-style-type: none; margin: 0; padding: 0; }
        .tree li { margin: 5px 0; padding-left: 20px; position: relative; }
        .tree li:before { content: '├── '; position: absolute; left: 0; }
        .tree li:last-child:before { content: '└── '; }
        .tree ul { margin-left: 20px; border-left: 1px solid #ccc; }
        .tree strong { color: #2c3e50; }
        .tree li li { color: #7f8c8d; }
        </style>
        """
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Project Tree</title>
            {css}
        </head>
        <body>
            {''.join(html_tree)}
        </body>
        </html>
        """
        
        response = HttpResponse(full_html, content_type='text/html')
        return response
        
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title></head>
        <body>
            <h3>Error generating project tree</h3>
            <p>{str(e)}</p>
        </body>
        </html>
        """
        return HttpResponse(error_html, content_type='text/html')

def project_tree_view(request):
    """API endpoint that returns project tree data as JSON with a proper root node."""
    # Get year and month from session
    selected_year = request.session.get('selected_year')
    selected_month = request.session.get('selected_month')
    
    # Filter out soft-deleted projects (only active projects) and by session year/month
    projects = Project.objects.filter(is_active=True).prefetch_related('resources', 'assign_project', 'poc')
    
    if selected_year and selected_month:
        projects = projects.filter(year=selected_year, month=selected_month)
    
    projects = projects.all()
    
    # Create project nodes
    project_nodes = []
    for project in projects:
        assign_project_name = project.assign_project.resource_name if project.assign_project else None
        # Filter out soft-deleted resources
        active_resources = [{"text": res.resource_name, "icon": "fas fa-user"} 
                           for res in project.resources.filter(is_active=True)]
        poc_value = project.poc.resource_name if project.poc else None
       
        project_node = {
            "text": f"{project.project_name} ({project.get_project_type_display()})",
            "icon": "fas fa-project-diagram",
            "children": [
                {
                    "text": f"📋 Assigned Resource: {assign_project_name}",
                    "icon": "fas fa-user-tie"
                } if assign_project_name else None,
                {
                    "text": f"👥 Resources ({len(active_resources)})",
                    "icon": "fas fa-users",
                    "children": active_resources,
                    "opened": True
                } if active_resources else None,
                {
                    "text": f"🎯 POC: {poc_value}",
                    "icon": "fas fa-id-card"
                } if poc_value else None
            ]
        }
        # Remove any None values from the children array
        project_node["children"] = [child for child in project_node["children"] if child is not None]
        project_nodes.append(project_node)
    
    # Create root node containing all projects
    root_tree = [{
        "text": "All Projects",
        "icon": "fas fa-sitemap",
        "opened": True,
        "children": project_nodes
    }]
    
    return JsonResponse(root_tree, safe=False)


def project_list_api(request):
    """API endpoint that returns a list of projects for selection."""
    # Get year and month from session
    selected_year = request.session.get('selected_year')
    selected_month = request.session.get('selected_month')
    
    projects = Project.objects.all()
    
    if selected_year and selected_month:
        projects = projects.filter(year=selected_year, month=selected_month)
    
    projects = projects.values('id', 'project_name', 'project_type')
    project_list = [
        {
            'id': p['id'],
            'name': p['project_name'],
            'type': dict(Project.PROJECT_TYPE_CHOICES)[p['project_type']] if p['project_type'] else 'Unknown'
        }
        for p in projects
    ]
    return JsonResponse(project_list, safe=False)

def project_tree_graphviz(request):
    """Legacy function - now redirects to Canvas-based tree visualization."""
    from django.shortcuts import redirect
    return redirect('projects:project_tree_visualization')


def attendance_home(request):
    # Get year and month from session (set by home page)
    year = request.session.get('selected_year')
    month = request.session.get('selected_month')
    
    # If no session values, redirect to home page to set them
    if not year or not month:
        return redirect('dashboard_home')
    
    # Filter by year and month from session
    resources = Resource.active_objects.filter(year=year, month=month)  # Only active resources
    projects = Project.active_objects.prefetch_related('resources').filter(year=year, month=month)  # Only active projects

    # Totals for resource
    total_working_days = sum(r.working_days for r in resources if r.working_days)
    total_present_days = sum(r.present_day for r in resources if r.present_day)
    total_present_hours = sum(r.present_hours for r in resources if r.present_hours)
    presence_percentage = (100 * total_present_days) / total_working_days if total_working_days > 0 else 0

    # Group projects by project type and calculate type totals
    grouped_projects = defaultdict(list)
    type_totals = defaultdict(lambda: {
        'present_day': 0,
        'billable_days': 0,
        'non_billable_days': 0,
        'billable_hours': 0,
        'non_billable_hours': 0,
    })

    for p in projects:
        display_type = p.get_project_type_display()
        grouped_projects[display_type].append(p)
        type_totals[display_type]['present_day'] += p.present_day or 0
        type_totals[display_type]['billable_days'] += p.billable_days or 0
        type_totals[display_type]['non_billable_days'] += p.non_billable_days or 0
        type_totals[display_type]['billable_hours'] += p.billable_hours or 0
        type_totals[display_type]['non_billable_hours'] += p.non_billable_hours or 0

    # Grand totals for all projects
    total_project_present_day = sum(p.present_day or 0 for p in projects)
    total_project_billable_days = sum(p.billable_days or 0 for p in projects)
    total_project_non_billable_days = sum(p.non_billable_days or 0 for p in projects)
    total_project_billable_hours = sum(p.billable_hours or 0 for p in projects)
    total_project_non_billable_hours = sum(p.non_billable_hours or 0 for p in projects)

    # Calculate team productivity hours (sum of all billable hours across all project types)
    team_productivity_hours = sum(p.billable_hours or 0 for p in projects)

    # Calculate team productivity percentage (100 × Team Productivity Hours / Expected Billable Hours)
    # expected_hours = total_project_billable_days * 8
    expected_hours = total_present_hours
    if expected_hours > 0:
        team_productivity_percentage = (100 * team_productivity_hours) / expected_hours
    else:
        team_productivity_percentage = 0

    # Clamp to [0, 100] to avoid negative or >100 values
    team_productivity_percentage = max(0, min(100, team_productivity_percentage))
    not_productive_percentage = 100 - team_productivity_percentage

    # --- PIE CHART GENERATION FOR OVERALL PRODUCTIVITY ---
    pie_chart_base64 = None
    try:
        # Only generate chart if we have meaningful data
        if team_productivity_hours > 0 or expected_hours > 0:
            labels = ['Productive', 'Not Productive']
            sizes = [team_productivity_percentage, not_productive_percentage]
            colors = ['#4CAF50', '#FF5252']
            
            # Create figure with specific size and DPI for better quality
            fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
            ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            plt.title('Team Productivity Percentage', fontsize=14, fontweight='bold')
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', facecolor='white', edgecolor='none')
            plt.close(fig)
            buf.seek(0)
            pie_chart_base64 = base64.b64encode(buf.read()).decode('utf-8')
            buf.close()
            
    except ImportError as e:
        # Matplotlib not available
        print(f"Matplotlib not available: {e}")
        pie_chart_base64 = None
    except Exception as e:
        # Other matplotlib errors
        print(f"Error generating pie chart: {e}")
        pie_chart_base64 = None

    context = {
        'resources': resources,
        'projects': projects,
        'grouped_projects': dict(grouped_projects),
        'type_totals': dict(type_totals),
        'total_working_days': total_working_days,
        'total_present_days': total_present_days,
        'total_present_hours': total_present_hours,
        'total_project_present_day': total_project_present_day,
        'total_project_billable_days': total_project_billable_days,
        'total_project_non_billable_days': total_project_non_billable_days,
        'total_project_billable_hours': total_project_billable_hours,
        'total_project_non_billable_hours': total_project_non_billable_hours,
        'presence_percentage': presence_percentage,
        'team_productivity_percentage': team_productivity_percentage,
        'not_productive_percentage': not_productive_percentage,
        'team_productivity_hours': team_productivity_hours,
        'pie_chart_base64': pie_chart_base64,
        'year': year,
        'month': month,
    }

    return render(request, 'attendance/attendance_home.html', context)
