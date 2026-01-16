from django.db import transaction
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from apps.usuarios.decorators import permiso_required, permiso_required_cbv, permiso_excluido, permiso_excluido_cbv
from .forms import form_crear_primera_vuelta, form_crear_urna, form_registrar_candidato, form_consultar_resultados, form_votar, form_crear_segunda_vuelta
from .models import Periodo, Elecciones, Urna, Candidato, Voto, Sufragio
from .utils import crear_usuario_permiso_persona_urna, crear_votos_urna, crear_urnas_segunda_vuelta

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
    numero_votantes = padron.count()

    context = {
        'urna': urna,
        'password': password,
        'padron': padron,
        'numero_votantes': numero_votantes
    }

    return render(request, "tarjeta_urna.html", context)

# REGISTRAR CANDIDATO
@permiso_required_cbv('admin', 'elecciones')
class registrar_candidato(LoginRequiredMixin,FormView):
    
    form_class = form_registrar_candidato
    template_name = 'form_registrar_candidato.html'
    success_url = reverse_lazy('registrar_candidato')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        elecciones_activas = Elecciones.objects.filter(activas=True).first()
        context['elecciones_activas'] = elecciones_activas
        context['candidatos_jefe'] = Candidato.objects.filter(elecciones=elecciones_activas, tipo='JCM')
        context['candidatas_jefa'] = Candidato.objects.filter(elecciones=elecciones_activas, tipo='JCF')
        context['candidatos_mats'] = Candidato.objects.filter(elecciones=elecciones_activas, tipo='JM')
        return context

    def form_valid(self, form):

        try:
            with transaction.atomic():

                candidatos = form.cleaned_data['persona'] 

                for candidato in candidatos:

                    nuevo_candidato, created = Candidato.objects.get_or_create(
                        persona=candidato,
                        tipo=form.cleaned_data['tipo'],
                        elecciones=form.cleaned_data['elecciones']
                    )

                    if not created:
                        messages.error(self.request, f'{nuevo_candidato.persona.nombre} ya es candidato(a).')

            messages.success(self.request, 'Candidato(s) registrado(s) correctamente.')

        except Exception as e:
            form.add_error(None, f'Ocurrió un error al registrar al candidato. {e}')
            return self.form_invalid(form)

        return super().form_valid(form)
    
# VER RESULTADOS
@permiso_required_cbv('admin', 'director', 'secretaria')
class consultar_resultados(LoginRequiredMixin, FormView):

    form_class = form_consultar_resultados
    template_name = 'form_consultar_resultados.html'

    def form_valid(self, form):
        elecciones = form.cleaned_data['elecciones']
        return redirect('reporte_elecciones', elecciones_id=elecciones.id)
    
# REPORTE DE RESULTADOS
@login_required
@permiso_required('admin', 'director', 'secretaria')
def reporte_elecciones(request, elecciones_id):

    elecciones = get_object_or_404(Elecciones, id=elecciones_id)

    empadronados = Voto.objects.filter(urna__elecciones=elecciones).count()

    sufragios = Sufragio.objects.filter(elecciones=elecciones).count()

    candidatos_jefe = Candidato.objects.filter(elecciones=elecciones, tipo='JCM')

    for jcm in candidatos_jefe:
        jcm.votos = Sufragio.objects.filter(voto_jefe=jcm, elecciones=elecciones).count()

    nulos_jefe = Sufragio.objects.filter(voto_jefe=None).count()

    candidatas_jefa = Candidato.objects.filter(elecciones=elecciones, tipo='JCF')

    for jcf in candidatas_jefa:
        jcf.votos = Sufragio.objects.filter(voto_jefa=jcf, elecciones=elecciones).count()
    
    nulos_jefa = Sufragio.objects.filter(voto_jefa=None).count()

    candidatos_mats = Candidato.objects.filter(elecciones=elecciones, tipo='JM')

    for jm in candidatos_mats:
        jm.votos = Sufragio.objects.filter(voto_materiales=jm, elecciones=elecciones).count()

    nulos_mats = Sufragio.objects.filter(voto_materiales=None).count()
    
    context = {
        'elecciones': elecciones,
        'empadronados': empadronados,
        'sufragios': sufragios,

        'candidatos_jefe': candidatos_jefe,
        'candidatas_jefa': candidatas_jefa,
        'candidatos_mats': candidatos_mats,

        'nulos_jefe': nulos_jefe,
        'nulos_jefa': nulos_jefa,
        'nulos_mats': nulos_mats,
    }

    return render(request, "reporte_elecciones.html", context)

# REPORTE DE RESULTADOS
@login_required
@permiso_required('urna')
def autorizar_voto(request):

    urna = request.user.urna_usuario

    votos = urna.votos_urna.select_related('persona').only(
        'persona__id',
        'persona__cedula',
        'persona__nombre',
        'persona__apellido',
        'persona__area__nombre',
        'permitido',
        'completo'
    ).order_by('persona__apellido')

    context = {
        'urna': urna,
        'votos': votos
    }

    return render(request, "autorizar_voto.html", context)

# PERMITIR VOTO
@login_required
@permiso_required('urna')
def permitir_voto(request, voto_id):

    urna = request.user.urna_usuario
    votos = urna.votos_urna.all()
    
    for v in votos:
        v.permitido = False
        v.save()

    voto = get_object_or_404(Voto, id=voto_id)
    voto.permitido = True
    voto.save()

    return redirect('autorizar_voto')

# VOTO PERMITIDO ACTUAL
@login_required
@permiso_required('urna')
def voto_permitido_actual(request):

    urna = request.user.urna_usuario
    voto_permitido_actual = urna.votos_urna.filter(permitido=True).first()

    if not voto_permitido_actual:
        messages.error(request, 'Aún no se ha autorizado ningún voto en esta urna.')
        return redirect('listo_para_votar')
    else:
        print(f"El ID del voto permitido actual en la urna {urna.usuario.username} es: {voto_permitido_actual.id}")
        return redirect('votar', voto_id=voto_permitido_actual.id)
    
# LISTO PARA VOTAR?
@login_required
@permiso_required('urna')
def listo_para_votar(request):

    return render(request, 'listo_para_votar.html')

# VOTAR
@login_required
@permiso_required('urna')
def votar(request, voto_id):

    form = form_votar(data=request.POST or None)

    user = request.user

    voto = get_object_or_404(Voto, id=voto_id)

    if voto.urna.usuario != user:
        print(f"Este voto corresponde a la {voto.urna.usuario} pero {user} intentó acceder.")
        messages.error(request, 'Este voto no corresponde a esta urna.')
        return redirect('listo_para_votar')

    if voto.completo:
        print(f"{voto.persona} intentó registrar su voto otra vez.")
        messages.error(request, f'{voto.persona} ya votó.')
        return redirect('listo_para_votar')

    if not voto.permitido:
        print(f"{voto.persona} intentó votar aunque no estuviese autorizado.")
        messages.error(request, f'{voto.persona} aún no puede votar.')
        return redirect('listo_para_votar')
    
    elecciones = Elecciones.objects.filter(activas=True).first()

    candidatos_jefe = Candidato.objects.filter(elecciones=elecciones, tipo='JCM').select_related('persona').only(
        'persona__nombre',
        'persona__apellido',
        'persona__foto',
    )

    radios_jefe = zip(form['voto_jefe'], candidatos_jefe)

    candidatas_jefa = Candidato.objects.filter(elecciones=elecciones, tipo='JCF').select_related('persona').only(
        'persona__nombre',
        'persona__apellido',
        'persona__foto',
    )

    radios_jefa = zip(form['voto_jefa'], candidatas_jefa)

    candidatos_mats = Candidato.objects.filter(elecciones=elecciones, tipo='JM').select_related('persona').only(
        'persona__nombre',
        'persona__apellido',
        'persona__foto',
    )

    radios_mats = zip(form['voto_materiales'], candidatos_mats)

    if request.method == 'POST':

        if form.is_valid():

            try:
                with transaction.atomic():

                    voto.completo = True
                    print(f"{voto.persona} registró su voto.")
                    voto.permitido = False
                    print(f"El voto de {voto.persona} ha sido bloqueado.")

                    nuevo_voto_jefe=form.cleaned_data['voto_jefe']
                    nuevo_voto_jefa=form.cleaned_data['voto_jefa']
                    nuevo_voto_materiales=form.cleaned_data['voto_materiales']

                    Sufragio.objects.create(
                        elecciones=voto.urna.elecciones,
                        voto_jefe=nuevo_voto_jefe,
                        voto_jefa=nuevo_voto_jefa,
                        voto_materiales=nuevo_voto_materiales
                    )

                    print("======================================")
                    if nuevo_voto_jefe == None:
                        print("Voto nulo para jefe de campamento.")
                    else:
                        print(f"{nuevo_voto_jefe.persona} recibió un voto.")

                    if nuevo_voto_jefa == None:
                        print("Voto nulo para jefa de campamento.")
                    else:
                        print(f"{nuevo_voto_jefa.persona} recibió un voto.")

                    if nuevo_voto_materiales == None:
                        print("Voto nulo para jefe de materiales.")
                    else:
                        print(f"{nuevo_voto_materiales.persona} recibió un voto." or None)
                    print("======================================")

                    voto.save()
                
                messages.success(request, 'Voto registrado correctamente')
                return redirect('listo_para_votar')
            
            except Exception as e:
                messages.error(None, f'Ocurrió un error al registrar tu voto. {e}')
                return redirect('listo_para_votar')

    context = {
        'voto': voto,
        'radios_jefe': radios_jefe,
        'radios_jefa': radios_jefa,
        'radios_mats': radios_mats,
        'form': form
    }

    return render(request, 'votar.html', context)

# CREAR SEGUNDA VUELTA
@permiso_required_cbv('admin', 'elecciones')
class crear_segunda_vuelta(LoginRequiredMixin,FormView):
    
    form_class = form_crear_segunda_vuelta
    template_name = 'form_crear_segunda_vuelta.html'
    success_url = reverse_lazy('registrar_candidato')

    def form_valid(self, form):

        try:
            with transaction.atomic():

                elecciones_primera_vuelta = form.cleaned_data['elecciones']
                
                elecciones_primera_vuelta.activas=False

                if Elecciones.objects.filter(periodo=elecciones_primera_vuelta.periodo, tipo=2).exists():
                    messages.error(self.request, 'Ya existe segunda vuelta para este periodo.')
                    return redirect('crear_segunda_vuelta')
                
                elecciones_primera_vuelta.save()

                elecciones_segunda_vuelta=Elecciones.objects.create(
                    periodo=elecciones_primera_vuelta.periodo,
                    tipo=2
                )

                urnas_primera_vuelta=Urna.objects.filter(elecciones=elecciones_primera_vuelta)

                crear_urnas_segunda_vuelta(elecciones_segunda_vuelta, urnas_primera_vuelta)

                transaction.set_rollback(True)

            messages.success(self.request, 'Segunda vuelta creada correctamente.')

        except Exception as e:
            form.add_error(None, f'Ocurrió un error al crear la segunda vuelta de elecciones. {e}')
            return self.form_invalid(form)

        return super().form_valid(form)


