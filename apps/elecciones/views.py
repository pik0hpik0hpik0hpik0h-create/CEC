from django.db import transaction
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from apps.usuarios.decorators import permiso_required, permiso_required_cbv, permiso_excluido, permiso_excluido_cbv
from .forms import form_crear_primera_vuelta, form_crear_urna, form_registrar_candidato, form_consultar_resultados, form_votar
from .models import Periodo, Elecciones, Urna, Candidato, Voto
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

    votantes = Voto.objects.filter(urna__elecciones=elecciones).count()

    sufragios = Voto.objects.filter(completo=True).count()

    candidatos_jefe = Candidato.objects.filter(elecciones=elecciones, tipo='JCM')

    for jcm in candidatos_jefe:
        jcm.votos = Voto.objects.filter(voto_jefe=jcm, urna__elecciones=elecciones).count()

    candidatas_jefa = Candidato.objects.filter(elecciones=elecciones, tipo='JCF')

    for jcf in candidatas_jefa:
        jcf.votos = Voto.objects.filter(voto_jefa=jcf, urna__elecciones=elecciones).count()

    candidatos_mats = Candidato.objects.filter(elecciones=elecciones, tipo='JM')

    for jm in candidatos_mats:
        jm.votos = Voto.objects.filter(voto_materiales=jm, urna__elecciones=elecciones).count()
    
    context = {
        'elecciones': elecciones,
        'votantes': votantes,
        'sufragios': sufragios,

        'candidatos_jefe': candidatos_jefe,
        'candidatas_jefa': candidatas_jefa,
        'candidatos_mats': candidatos_mats
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

            voto.completo = True
            print(f"{voto.persona} registró su voto.")
            voto.permitido = False
            print(f"El voto de {voto.persona} ha sido bloqueado.")

            voto_jefe=form.cleaned_data['voto_jefe']
            voto_jefa=form.cleaned_data['voto_jefa']
            voto_materiales=form.cleaned_data['voto_materiales']

            print("======================================")
            print(f"{voto_jefe.persona} recibió un voto.")
            print(f"{voto_jefa.persona} recibió un voto.")
            print(f"{voto_materiales.persona} recibió un voto.")
            print("======================================")

            #voto.save()

            messages.success(request, 'Voto registrado correctamente')
            return redirect('listo_para_votar')

    context = {
        'voto': voto,
        'radios_jefe': radios_jefe,
        'radios_jefa': radios_jefa,
        'radios_mats': radios_mats,
        'form': form
    }

    return render(request, 'votar.html', context)


