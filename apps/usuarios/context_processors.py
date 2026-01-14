from django.conf import settings
from .models import Persona

def debug_status(request):
    return {
        'debug': settings.DEBUG
    }

def usuario_actual(request):
    if request.user.is_authenticated:
        try:
            persona = Persona.objects.get(usuario=request.user)
            return {
                'usuario_persona': persona,
                'usuario_nombre': persona.nombre,
                'usuario_apellido': persona.apellido,
                'usuario_nombre_completo': f"{persona.nombre} {persona.apellido}",
                'usuario_foto': persona.foto.url if persona.foto else None,
            }
        except Persona.DoesNotExist:
            pass

    return {}


def permisos_context(request):
   
    permisos = []

    if request.user.is_authenticated:
        
        if hasattr(request.user, 'permisos'):
            permisos = request.user.permisos.values_list('permiso__slug', flat=True)

    return {'permisos_usuario': permisos}