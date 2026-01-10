from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from apps.usuarios.forms import form_login, form_registrar_usuario
from .models import Persona

class login_view(LoginView):
    template_name = 'login.html'
    authentication_form = form_login
    redirect_authenticated_user = True
    next_page = reverse_lazy('dashboard')

def dashboard_usuarios(request):

    return render(request, "dashboard_usuarios.html")

class registrar_usuario(FormView):
    model = Persona
    form_class = form_registrar_usuario
    template_name = 'form_registrar_usuario.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.save()  
        return super().form_valid(form)




