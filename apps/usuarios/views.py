import csv
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView
import io
from apps.usuarios.forms import form_login, form_registrar_usuario, form_registrar_usuario_csv, form_nueva_clave, form_editar_perfil
from core.funciones_generales.utils import ahora
from apps.usuarios.decorators import permiso_required, permiso_required_cbv
from apps.usuarios.utils import crear_usuario
from .models import Area, Persona

# LOGIN
class login_view(LoginView):
    template_name = 'login.html'
    authentication_form = form_login
    redirect_authenticated_user = True
    next_page = reverse_lazy('dashboard')

# INGRESAR NUEVA CONTRASEÑA
@login_required
def ingresar_nueva_clave(request):

    form = form_nueva_clave(user=request.user, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()  

            persona = request.user.persona
            persona.clave_temporal = False
            persona.save()

            update_session_auth_hash(request, request.user)

            messages.success(request, 'Contraseña actualizada correctamente')
            return redirect('dashboard')

    return render(request, 'ingresar_nueva_clave.html', {'form': form})


# DASHBOARD DE USUARIOS
@login_required
@permiso_required('admin', 'secretaria')
def dashboard_usuarios(request):

    return render(request, "dashboard_usuarios.html")

# FORMULARIO DE REGISTRO DE USUARIO
@permiso_required_cbv('admin', 'secretaria')
class registrar_usuario(LoginRequiredMixin, FormView):
    
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
@login_required
@permiso_required('admin', 'secretaria')
def tarjeta_registrar_usuario(request, persona_id):

    persona = get_object_or_404(Persona, id=persona_id)
    password = request.session.pop('password_temporal', None)

    context = {
        'persona': persona,
        'password_temporal': password
    }

    return render(request, "tarjeta_registrar_usuario.html", context)

# REGISTRO DE USUARIOS CON CSV
@login_required
@permiso_required('admin')
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

                        persona.save()
                        
                        print("==============================================")
                        print(persona.nombre + " " + persona.apellido)
                        print(usuario)

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

                    messages.error(request,f"Error en cédula {fila.get('cedula')}: {str(e)}")

            request.session['reporte_usuarios'] = personas_creadas

            messages.success(request, f"Se cargaron {len(personas_creadas)} usuarios correctamente")

            return redirect('reporte_usuarios_csv')

    else:
        form = form_registrar_usuario_csv()

    return render(request, 'form_registrar_usuario_csv.html', {'form': form})

# REPORTE DE REGISTRO DE PERSONAS CON CSV
@login_required
@permiso_required('admin')
def reporte_usuarios_csv(request):

    registros = request.session.get('reporte_usuarios', [])

    if not registros:
        return redirect('registrar_usuarios_csv')

    context = {
        'registros': registros,
        'ahora': ahora
    }

    return render(request, 'reporte_usuarios_csv.html', context)

# LIMPIAR REPORTE
@login_required
@permiso_required('admin')
def limpiar_reporte_csv(request):

    request.session.pop('reporte_usuarios', None)

    return redirect('dashboard_usuarios')

#EDITAR PERFIL
@login_required
def editar_perfil(request):

    persona = request.user.persona

    if request.method == 'POST':

        form = form_editar_perfil(request.POST, request.FILES, instance=persona)

        if form.is_valid():

            form.save()

            messages.success(request, 'Información actualizada correctamente.')
            return redirect('dashboard')

    else:
        form = form_editar_perfil(instance=persona)

    return render(request, 'form_editar_perfil.html', {'form': form})


