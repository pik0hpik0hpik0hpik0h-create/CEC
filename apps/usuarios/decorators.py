from django.shortcuts import redirect
from django.contrib import messages

def permiso_required(*permisos_necesarios):
   
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                messages.error(request, "Debes iniciar sesión")
                return redirect('login')

            user_permisos = user.permisos.values_list('permiso__slug', flat=True)
            if not any(p in user_permisos for p in permisos_necesarios):
                messages.error(request, "No tienes permiso para acceder aquí")
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def permiso_required_cbv(*permisos_necesarios):
   
    def decorator(view_class):
        original_dispatch = view_class.dispatch

        def new_dispatch(self, request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                 
                messages.error(request, "Debes iniciar sesión")
                return redirect('login')

            user_permisos = user.permisos.values_list('permiso__slug', flat=True)
            if not any(p in user_permisos for p in permisos_necesarios):
                 
                messages.error(request, "No tienes permiso para acceder aquí")
                return redirect('dashboard')

            return original_dispatch(self, request, *args, **kwargs)

        view_class.dispatch = new_dispatch
        return view_class
    return decorator

def permiso_excluido(*permisos_bloqueados):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect('login')

            user_permisos = user.permisos.values_list('permiso__slug', flat=True)

            if any(p in user_permisos for p in permisos_bloqueados):
                messages.error(request, "No tienes acceso a esta sección")
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def permiso_excluido_cbv(*permisos_bloqueados):
    
    def decorator(view_class):
        original_dispatch = view_class.dispatch

        def new_dispatch(self, request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect('login')

            user_permisos = user.permisos.values_list('permiso__slug', flat=True)

            if any(p in user_permisos for p in permisos_bloqueados):
                messages.error(request, "No tienes acceso a esta sección")
                return redirect('dashboard')

            return original_dispatch(self, request, *args, **kwargs)

        view_class.dispatch = new_dispatch
        return view_class

    return decorator