from django.shortcuts import redirect
from django.urls import reverse
from apps.usuarios.models import Persona

class forza_cambio_clave_middleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            clave_temporal = Persona.objects.filter(
                user=request.user
            ).values_list('clave_temporal', flat=True).first()

            if clave_temporal:
                rutas_permitidas = [
                    reverse('ingresar_nueva_clave'),
                    reverse('logout'),
                ]

                if request.path not in rutas_permitidas:
                    return redirect('ingresar_nueva_clave')

        return self.get_response(request)
