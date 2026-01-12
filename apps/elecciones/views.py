from django.db import transaction
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import FormView
from .forms import form_crear_primera_vuelta
from .models import Periodo, Elecciones


def dashboard_elecciones(request):
 
    return render(request, "dashboard_elecciones.html")

def dashboard_crear_elecciones(request):

    return render(request, "dashboard_crear_elecciones.html")

# CREAR PRIMERA VUELTA
class crear_primera_vuelta(FormView):
    
    form_class = form_crear_primera_vuelta
    template_name = 'form_crear_primera_vuelta.html'
    success_url = reverse_lazy('crear_primera_vuelta')

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

                self.elecciones_id = elecciones.id

            messages.success(self.request, 'Primera vuelta creada correctamente.')

        except Exception as e:
            form.add_error(None, f'Ocurrió un error al crear la primera vuelta de elecciones. {e}')
            return self.form_invalid(form)

        return super().form_valid(form)
    
    #def get_success_url(self):
        #return reverse('form_crear_urnas.html', kwargs={'elecciones_id': self.elecciones_id})
    
