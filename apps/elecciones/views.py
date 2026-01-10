from django.shortcuts import render

def dashboard_elecciones(request):

    return render(request, "dashboard_elecciones.html")

def dashboard_crear_elecciones(request):

    return render(request, "dashboard_crear_elecciones.html")

def crear_primera_vuelta(request):

    return render(request, "form_crear_primera_vuelta.html")
