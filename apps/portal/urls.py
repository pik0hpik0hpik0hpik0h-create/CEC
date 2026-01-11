from django.urls import path
from . import views
from apps.usuarios.views import login_view, ingresar_nueva_clave

urlpatterns = [
    path("", views.inicio, name="inicio"), 
    path("ingreso/", login_view.as_view(), name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),  
    path("nueva_clave/", ingresar_nueva_clave, name="ingresar_nueva_clave"), 
]
