from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    # Dashboard routes
    path("", views.dashboard_home, name="home"),
    path("dashboard/", views.dashboard_home, name="dashboard_home"),
    path("attendance/", views.attendance_home, name="attendance_home"),
    
    # Project CRUD routes
    path("projects/", views.project_list, name="project_list"),
    path("projects/create/", views.project_create, name="project_create"),
    path("projects/edit/<int:pk>/", views.project_edit, name="project_edit"),
    path("projects/delete/<int:pk>/", views.project_delete, name="project_delete"),
    
    # Tree visualization routes
    path("project-tree/", views.project_tree_view, name="project_tree"),
    path("project-list-api/", views.project_list_api, name="project_list_api"),
    path("project-canvas-tree/", views.project_canvas_tree_visualization, name="project_canvas_tree_visualization"),
]