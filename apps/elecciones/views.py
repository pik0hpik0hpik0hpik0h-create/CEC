from django.db import transaction
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from apps.usuarios.decorators import permiso_required, permiso_required_cbv, permiso_excluido, permiso_excluido_cbv
from .forms import form_crear_primera_vuelta, form_crear_urna
from .models import Periodo, Elecciones, Urna
from .utils import crear_usuario_permiso_persona_urna, crear_votos_urna

@login_required
def dashboard_elecciones(request):
 
    return render(request, "dashboard_elecciones.html")

@login_required
@permiso_required('admin', 'elecciones')
def dashboard_crear_elecciones(request):

    return render(request, "dashboard_crear_elecciones.html")

# CREAR PRIMERA VUELTA
@permiso_required_cbv('admin', 'elecciones')
class crear_primera_vuelta(LoginRequiredMixin,FormView):
    
    form_class = form_crear_primera_vuelta
    template_name = 'form_crear_primera_vuelta.html'
    success_url = reverse_lazy('crear_urna')

    def form_valid(self, form):

        try:
            with transaction.atomic():

                elecciones = form.save(commit=False)

                elecciones.tipo = 1

                periodo_activo = Periodo.objects.filter(activo=True).first()

                if Elecciones.objects.filter(periodo=periodo_activo, tipo=1).exists():
                    messages.error(self.request, 'Ya existe primera vuelta para este periodo.')
                    return redirect('crear_primera_vuelta')

                elecciones.save()

            messages.success(self.request, 'Primera vuelta creada correctamente.')

        except Exception as e:
            form.add_error(None, f'Ocurrió un error al crear la primera vuelta de elecciones. {e}')
            return self.form_invalid(form)

        return super().form_valid(form)
    
# CREAR URNA
@permiso_required_cbv('admin', 'elecciones')
class crear_urna(LoginRequiredMixin,FormView):
    
    form_class = form_crear_urna
    template_name = 'form_crear_urna.html'

    def form_valid(self, form):

        try:
            with transaction.atomic():

                urna = form.save(commit=False)

                elecciones_activas = Elecciones.objects.filter(activas=True).first()

                print("Creando urna: " + urna.area.nombre + " " + urna.genero)

                user, password, persona = crear_usuario_permiso_persona_urna(urna)

                if Urna.objects.filter(elecciones=elecciones_activas, genero=urna.genero, area=urna.area).exists():
                    messages.error(self.request, 'Ya existe una urna de este tipo para estas elecciones.')
                    return redirect('crear_urna')
                
                urna.usuario = user
                urna.save()

                self.request.session['password'] = password

                self.urna_id = urna.id

                crear_votos_urna(urna, persona)
            
            messages.success(self.request, 'Urna creada correctamente.')

        except Exception as e:
            form.add_error(None, f'Ocurrió un error al crear la urna. {e}')
            return self.form_invalid(form)

        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('tarjeta_urna', kwargs={'urna_id': self.urna_id})

# TARJETA DE DATOS DE PERSONA
@login_required
@permiso_required('admin', 'elecciones')
def tarjeta_urna(request, urna_id):

    urna = get_object_or_404(Urna, id=urna_id)
    password = request.session.pop('password', None)
    padron = urna.votos_urna.all().order_by('persona__apellido')

    context = {
        'urna': urna,
        'password': password,
        'padron': padron 
    }

    return render(request, "tarjeta_urna.html", context)
    
