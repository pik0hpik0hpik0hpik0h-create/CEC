from django.shortcuts import render

def inicio(request):

    return render(request, "inicio.html")

def login(request):
    
    return render(request, "login.html")

def dashboard(request):

    return render(request, "dashboard.html")