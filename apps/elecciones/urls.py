from django.urls import path
from . import views
 
urlpatterns = [
    path("", views.dashboard_elecciones, name="dashboard_elecciones"), 
    path("crear/", views.dashboard_crear_elecciones, name="dashboard_crear_elecciones"), 
    path("crear/primera_vuelta", views.crear_primera_vuelta.as_view(), name="crear_primera_vuelta"),
    path("crear/urna", views.crear_urna.as_view(), name="crear_urna"),  
    path("crear/urna/tarjeta/<int:urna_id>/", views.tarjeta_urna, name="tarjeta_urna"),  
    path("registrar/candidato/", views.registrar_candidato.as_view(), name="registrar_candidato")
]
