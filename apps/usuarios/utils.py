from django.contrib.auth.models import User  
from django.utils.crypto import get_random_string

def crear_usuario(persona):

    nombre = persona.nombre.strip().split()[0].lower()
    apellido = persona.apellido.strip().split()[0].lower()

    base = f"{nombre}{apellido}{persona.cedula[-4:]}"
    username = base

    i = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{i}"
        i += 1

    password_temporal = get_random_string(8)

    user = User.objects.create_user(username=username, password=password_temporal)

    persona.usuario = user

    return user, password_temporal
