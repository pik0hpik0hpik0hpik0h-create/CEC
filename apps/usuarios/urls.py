from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
 
urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path("", views.dashboard_usuarios, name="dashboard_usuarios"), 
    path("registrar/", views.registrar_usuario.as_view(), name="registrar_usuario"),
    path("tarjeta/<int:persona_id>/", views.tarjeta_registrar_usuario, name="tarjeta_registrar_usuario"),
    path("registrar_csv/", views.registrar_usuarios_csv, name="registrar_usuarios_csv"),
    path("reporte_csv/", views.reporte_usuarios_csv, name="reporte_usuarios_csv"),
]
