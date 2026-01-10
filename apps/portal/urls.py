from django.urls import path
from . import views
from apps.usuarios.views import login_view

urlpatterns = [
    path("", views.inicio, name="inicio"), 
    path("ingreso/", login_view.as_view(), name="login"),
    path("dashboard/", views.dashboard, name="dashboard"), 
]
