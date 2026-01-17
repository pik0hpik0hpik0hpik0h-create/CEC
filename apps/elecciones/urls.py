from django.urls import path
from . import views
 
urlpatterns = [
    path("", views.dashboard_elecciones, name="dashboard_elecciones"), 
    path("crear/", views.dashboard_crear_elecciones, name="dashboard_crear_elecciones"), 
    path("crear/primera_vuelta", views.crear_primera_vuelta.as_view(), name="crear_primera_vuelta"),
    path("crear/urna", views.crear_urna.as_view(), name="crear_urna"),  
    path("crear/urna/tarjeta/<int:urna_id>/", views.tarjeta_urna, name="tarjeta_urna"),  
    path("registrar/candidato/", views.registrar_candidato.as_view(), name="registrar_candidato"),
    path("resultados/", views.consultar_resultados.as_view(), name="consultar_resultados"),
    path("resultados/reporte/<int:elecciones_id>/", views.reporte_elecciones, name="reporte_elecciones"),
    path("autorizar_voto/", views.autorizar_voto, name="autorizar_voto"),
    path("permitir_voto/<int:voto_id>/", views.permitir_voto, name="permitir_voto"),
    path("voto_permitido_actual/", views.voto_permitido_actual, name="voto_permitido_actual"),
    path("listo/", views.listo_para_votar, name="listo_para_votar"),
    path("votar/<int:voto_id>/", views.votar, name="votar"),
    path("crear/segunda_vuelta", views.crear_segunda_vuelta.as_view(), name="crear_segunda_vuelta"),
    path("elecciones_actuales/", views.elecciones_actuales, name="elecciones_actuales"),
    path("tarjeta/<int:elecciones_id>/", views.tarjeta_elecciones, name="tarjeta_elecciones"),
]
