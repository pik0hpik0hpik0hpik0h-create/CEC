from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def inicio(request):

    return render(request, "inicio.html")

@login_required
def dashboard(request):

    return render(request, "dashboard.html")