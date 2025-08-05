from collections import defaultdict
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from datetime import datetime
from .models import Project
from .forms import ProjectForm
from resources.models import Resource
from anytree import Node, RenderTree
from anytree.exporter import DotExporter
from io import BytesIO
import graphviz
import os
# Set Graphviz path for Windows
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"
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
    # Store in session for resource creation
    if year_param and month_param:
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
    years = list(Project.active_objects.values_list('year', flat=True).distinct())
    months = list(Project.active_objects.values_list('month', flat=True).distinct())
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    projects = Project.active_objects.all()  # Only show active projects
    if selected_year:
        projects = projects.filter(year=selected_year)
    if selected_month:
        projects = projects.filter(month=selected_month)
    return render(request, 'projects/project_list.html', {
        'projects': projects,
        'years': years,
        'months': months,
        'selected_year': selected_year,
        'selected_month': selected_month,
    })


def project_create(request):
    if request.method == 'POST':
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            project_form.save()
            return redirect('projects:project_list')
    else:
        year = request.session.get('selected_year')
        month = request.session.get('selected_month')
        project_form = ProjectForm(initial={'year': year, 'month': month})

    return render(request, 'projects/project_form.html', {
        'form': project_form,
        'title': 'Create Project'
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


def project_tree_html(request):
    """Generate an HTML-based tree visualization that doesn't require Graphviz."""
    try:
        projects = Project.objects.prefetch_related('resources', 'assign_project', 'poc').all()
        
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
    """API endpoint that returns project tree data as JSON."""
    projects = Project.objects.prefetch_related('resources', 'assign_project', 'poc').all()
    tree = []
    for project in projects:
        assign_project_name = project.assign_project.resource_name if project.assign_project else None
        resource_names = [{"text": res.resource_name, "icon": "fas fa-user"} for res in project.resources.all()]
        poc_value = project.poc.resource_name if project.poc else None
       
        project_node = {
            "text": f"{project.project_name} ({project.get_project_type_display()})",
            "icon": "fas fa-project-diagram",
            "children": [
                {
                    "text": f"Assigned Resource: {assign_project_name}",
                    "icon": "fas fa-user-tie"
                } if assign_project_name else None,
                {
                    "text": f"Resources ({len(resource_names)})",
                    "icon": "fas fa-users",
                    "children": resource_names,
                    "opened": True
                } if resource_names else None,
                {
                    "text": f"POC: {poc_value}",
                    "icon": "fas fa-id-card"
                } if poc_value else None
            ]
        }
        # Remove any None values from the children array
        project_node["children"] = [child for child in project_node["children"] if child is not None]
        tree.append(project_node)
    return JsonResponse(tree, safe=False)


def project_list_api(request):
    """API endpoint that returns a list of projects for selection."""
    projects = Project.objects.all().values('id', 'project_name', 'project_type')
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
    """Generate a Graphviz visualization of the project tree."""
    try:
        # Check if a specific project is requested
        project_id = request.GET.get('project_id')
        
        if project_id:
            # Single project visualization
            try:
                project = Project.objects.prefetch_related('resources', 'assign_project', 'poc').get(pk=project_id)
                projects = [project]
                root_label = f"Project: {project.project_name}"
            except Project.DoesNotExist:
                return HttpResponse("Project not found", status=404)
        else:
            # All projects visualization
            projects = Project.objects.prefetch_related('resources', 'assign_project', 'poc').all()
            root_label = "All Projects"
        
        # Create root node for the tree
        root = Node(root_label)
        
        for project in projects:
            # Create project node
            if project_id:
                # For single project, make project the root
                project_node = root
            else:
                # For all projects, create project as child of root
                project_node = Node(f"{project.project_name}\n({project.get_project_type_display()})", parent=root)
            
            # Add assigned resource node
            if project.assign_project:
                Node(f"📋 Assigned Resource:\n{project.assign_project.resource_name}", parent=project_node)
            
            # Add resources node with children
            resources = project.resources.all()
            if resources:
                resources_node = Node(f"👥 Resources ({len(resources)})", parent=project_node)
                for res in resources:
                    Node(f"👤 {res.resource_name}", parent=resources_node)
            
            # Add POC node
            if project.poc:
                Node(f"🎯 POC:\n{project.poc.resource_name}", parent=project_node)
        
        # Generate Graphviz dot content with vertical layout and improved styling
        dot_content = []
        dot_content.append("digraph tree {")
        dot_content.append('    rankdir=TB;')  # Top to Bottom (vertical)
        dot_content.append('    node [shape=box, style="rounded,filled", fontname="Arial", fontsize=10];')
        dot_content.append('    edge [fontname="Arial", fontsize=8];')
        dot_content.append('    bgcolor=white;')
        dot_content.append('    dpi=150;')  # Higher DPI for better quality
        
        # Define colors for different node types
        colors = {
            'root': '#3498db',      # Blue for root
            'project': '#2ecc71',   # Green for projects
            'assigned': '#f39c12',  # Orange for assigned resources
            'resources': '#9b59b6', # Purple for resources group
            'resource': '#1abc9c',  # Teal for individual resources
            'poc': '#e74c3c'        # Red for POC
        }
        
        # Manually create the dot notation with colors
        node_counter = 0
        node_map = {}
        
        def add_node_to_dot(node, parent_id=None, node_type='default'):
            nonlocal node_counter
            current_id = f"node{node_counter}"
            node_map[node] = current_id
            node_counter += 1
            
            # Escape node name for DOT format and handle newlines
            node_name = str(node.name).replace('"', '\\"').replace('\n', '\\n')
            
            # Determine node type and color
            if node.parent is None:
                color = colors['root']
                node_type = 'root'
            elif '📋' in node.name:
                color = colors['assigned']
            elif '👥' in node.name:
                color = colors['resources']
            elif '👤' in node.name:
                color = colors['resource']
            elif '🎯' in node.name:
                color = colors['poc']
            elif node.parent and node.parent.parent is None:
                color = colors['project']
            else:
                color = '#ecf0f1'  # Light gray for others
            
            # Add node with color and styling
            dot_content.append(f'    {current_id} [label="{node_name}", fillcolor="{color}", fontcolor=white];')
            
            if parent_id:
                dot_content.append(f'    {parent_id} -> {current_id} [color="#34495e", penwidth=1.5];')
            
            # Process children
            for child in node.children:
                add_node_to_dot(child, current_id)
        
        add_node_to_dot(root)
        dot_content.append("}")
        
        # Create Graphviz source
        dot_source = "\n".join(dot_content)
        
        try:
            # Create and render the graph
            graph = graphviz.Source(dot_source)
            png_data = graph.pipe(format='png')
            
            # Return the image as HTTP response
            response = HttpResponse(png_data, content_type='image/png')
            response['Content-Disposition'] = 'inline; filename="project_tree.png"'
            return response
            
        except (graphviz.ExecutableNotFound, FileNotFoundError) as e:
            # Specific error for missing Graphviz executable
            error_msg = (
                "Graphviz executable not found. Please install Graphviz:\n"
                "Windows: Download from https://graphviz.org/download/ and add to PATH\n"
                "Or use: winget install graphviz\n\n"
                f"Error details: {str(e)}\n\n"
                "Fallback: Text representation of project tree:\n\n"
            )
            tree_text = [error_msg]
            for pre, _, node in RenderTree(root):
                tree_text.append(f"{pre}{node.name}")
            
            response = HttpResponse("\n".join(tree_text), content_type='text/plain')
            response['Content-Disposition'] = 'inline; filename="project_tree_error.txt"'
            return response
            
        except Exception as e:
            # General error handling
            error_msg = (
                f"Failed to generate Graphviz diagram: {str(e)}\n\n"
                "Fallback: Text representation of project tree:\n\n"
            )
            tree_text = [error_msg]
            for pre, _, node in RenderTree(root):
                tree_text.append(f"{pre}{node.name}")
            
            response = HttpResponse("\n".join(tree_text), content_type='text/plain')
            response['Content-Disposition'] = 'inline; filename="project_tree_fallback.txt"'
            return response
            
    except Exception as e:
        # Fallback for any other errors (database, etc.)
        error_msg = f"Error accessing project data: {str(e)}"
        response = HttpResponse(error_msg, content_type='text/plain')
        response['Content-Disposition'] = 'inline; filename="project_tree_error.txt"'
        return response


def attendance_home(request):
    # Get year and month from GET params, fallback to current year/month
    now = datetime.now()
    year_param = request.GET.get('year')
    month_param = request.GET.get('month')
    
    try:
        year = int(year_param) if year_param else now.year
    except (ValueError, TypeError):
        year = now.year
    
    try:
        month = int(month_param) if month_param else now.month
    except (ValueError, TypeError):
        month = now.month
    
    # Filter by year and month if provided
    resources = Resource.active_objects.all()  # Only active resources
    projects = Project.active_objects.prefetch_related('resources').all()  # Only active projects
    
    if year_param and month_param:
        resources = resources.filter(year=year, month=month)
        projects = projects.filter(year=year, month=month)

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
        'years': list(range(2020, 2031)),
        'months': [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ],
    }

    return render(request, 'attendance/attendance_home.html', context)
