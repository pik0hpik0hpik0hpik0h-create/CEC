from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_elecciones, name="dashboard_elecciones"), 
    path("crear/", views.dashboard_crear_elecciones, name="dashboard_crear_elecciones"), 
    path("crear/primera_vuelta", views.crear_primera_vuelta, name="crear_primera_vuelta"), 
]
