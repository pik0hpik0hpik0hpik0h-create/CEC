from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView
from apps.usuarios.forms import form_login, form_registrar_usuario
from apps.usuarios.utils import crear_usuario
from .models import Persona

class login_view(LoginView):
    template_name = 'login.html'
    authentication_form = form_login
    redirect_authenticated_user = True
    next_page = reverse_lazy('dashboard')

def dashboard_usuarios(request):

    return render(request, "dashboard_usuarios.html")

class registrar_usuario(FormView):
    
    form_class = form_registrar_usuario
    template_name = 'form_registrar_usuario.html'

    def form_valid(self, form):

        try:
            with transaction.atomic():
                
                persona = form.save(commit=False)

                user, password_temporal = crear_usuario(persona)

                persona.save()

                self.request.session['password_temporal'] = password_temporal
                self.persona_id = persona.id

        except Exception as e:
            form.add_error(None, 'Ocurrió un error al registrar el usuario.')
            return self.form_invalid(form)

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tarjeta_registrar_usuario', kwargs={'persona_id': self.persona_id})
    
def tarjeta_registrar_usuario(request, persona_id):

    persona = get_object_or_404(Persona, id=persona_id)
    password = request.session.pop('password_temporal', None)

    context = {
        'persona': persona,
        'password_temporal': password
    }

    return render(request, "tarjeta_registrar_usuario.html", context)




