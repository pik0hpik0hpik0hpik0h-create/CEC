import csv
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView
import io
import secrets
from apps.usuarios.forms import form_login, form_registrar_usuario, form_registrar_usuario_csv
from apps.usuarios.utils import crear_usuario
from .models import Area, Persona

# LOGIN
class login_view(LoginView):
    template_name = 'login.html'
    authentication_form = form_login
    redirect_authenticated_user = True
    next_page = reverse_lazy('dashboard')

# DASHBOARD DE USUARIOS
def dashboard_usuarios(request):

    return render(request, "dashboard_usuarios.html")

# FORMULARIO DE REGISTRO DE USUARIO
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
    
# TARJETA DE DATOS DE PERSONA
def tarjeta_registrar_usuario(request, persona_id):

    persona = get_object_or_404(Persona, id=persona_id)
    password = request.session.pop('password_temporal', None)

    context = {
        'persona': persona,
        'password_temporal': password
    }

    return render(request, "tarjeta_registrar_usuario.html", context)

def registrar_usuarios_csv(request):

    if request.method == 'POST':

        form = form_registrar_usuario_csv(request.POST, request.FILES)

        if form.is_valid():

            archivo = form.cleaned_data['archivo']

            data = archivo.read().decode('utf-8-sig')
        
            reader = csv.DictReader(
                io.StringIO(data),
                delimiter=';'
            )

            personas_creadas = []

            for i, fila in enumerate(reader, start=1):

                if not fila.get('cedula'):
                    continue

                fila = {k: v.strip() if v else v for k, v in fila.items()}

                try:
                    with transaction.atomic():

                        area = Area.objects.filter(nombre=fila['area']).first()

                        persona = Persona.objects.create(
                            cedula=fila['cedula'],
                            nombre=fila['nombre'],
                            apellido=fila['apellido'],
                            genero=fila['genero'],
                            fecha_nacimiento=fila['fecha_nacimiento'] or None,
                            area=area,
                        )


                        usuario, password_temporal = crear_usuario(persona)

                        personas_creadas.append({
                            'cedula': persona.cedula,
                            'nombre': persona.nombre,
                            'apellido': persona.apellido,
                            'genero': persona.genero,
                            'area': area.nombre if area else '',
                            'username': usuario.username,  
                            'password_temporal': password_temporal,  
                        })

                except Exception as e:

                    messages.error(
                        request,
                        f"Error en cédula {fila.get('cedula')}: {str(e)}"
                    )

            request.session['reporte_usuarios'] = personas_creadas

            messages.success(
                request,
                f"Se cargaron {len(personas_creadas)} usuarios correctamente"
            )

            return redirect('reporte_usuarios_csv')

    else:
        form = form_registrar_usuario_csv()

    return render(request, 'form_registrar_usuario_csv.html', {'form': form})


# REPORTE DE REGISTRO DE PERSONAS CON CSV
def reporte_usuarios_csv(request):

    registros = request.session.get('reporte_usuarios', [])

    if not registros:
        return redirect('registrar_usuarios_csv')

    context = {
        'registros': registros
    }

    return render(request, 'reporte_usuarios_csv.html', context)



