from django.urls import path
from . import views

app_name = "resources"

urlpatterns = [
    path("", views.resource_list, name="resource_list"),  # List all resources at /resources/
    path("create/", views.resource_create, name="resource_create"),
    path("update/<int:pk>/", views.resource_update, name="resource_update"),
    path("delete/<int:pk>/", views.resource_delete, name="resource_delete"),
    
    # Tree visualization routes
    path("resource-tree/", views.resource_tree_view, name="resource_tree"),
    path("resource-list-api/", views.resource_list_api, name="resource_list_api"),
    path("resource-canvas-tree/", views.resource_canvas_tree_visualization, name="resource_canvas_tree_visualization"),
]