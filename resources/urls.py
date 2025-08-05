from django.urls import path
from . import views

app_name = "resources"

urlpatterns = [
    path("", views.resource_list, name="resource_list"),  # List all resources at /resources/
    path("create/", views.resource_create, name="resource_create"),
    path("update/<int:pk>/", views.resource_update, name="resource_update"),
    path("delete/<int:pk>/", views.resource_delete, name="resource_delete"),
]