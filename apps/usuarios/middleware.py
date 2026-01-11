from django.shortcuts import redirect
from django.urls import reverse

class forza_cambio_clave_middleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if request.user.is_authenticated:
            persona = getattr(request.user, 'persona', None)

            if persona and persona.clave_temporal:
                rutas_permitidas = [
                    reverse('ingresar_nueva_clave'),
                    reverse('logout'),
                ]

                if request.path not in rutas_permitidas:
                    return redirect('ingresar_nueva_clave')

        return self.get_response(request)
