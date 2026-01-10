from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
 
urlpatterns = [
    path('logout/', LogoutView.as_view(), name='logout'),
    path("", views.dashboard_usuarios, name="dashboard_usuarios"), 
    path("registrar/", views.registrar_usuario.as_view(), name="registrar_usuario"),
]
