from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"), #PÁGINA PRINCIPAL
    path("ingreso", views.login, name="login"), #INICIO DE SESIÓN
    path("dashboard", views.dashboard, name="dashboard"), #DASHBOARD
]
