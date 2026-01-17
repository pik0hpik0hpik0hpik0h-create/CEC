from django.contrib.auth.models import User  
from django.utils.crypto import get_random_string
from apps.usuarios.models import Persona, Permiso, Permiso_Usuario, Area
from .models import Voto, Urna

def crear_usuario_permiso_persona_urna(urna):

    # CREAR USUARIO

    nombre_urna=f"Urna.{urna.area.nombre}.{urna.genero}"
    apellido_urna=f"{urna.elecciones.periodo.anio}.P{urna.elecciones.periodo.periodo}.V{urna.elecciones.tipo}"
    
    base = f"{nombre_urna}.{apellido_urna}"
    username = base

    i = 1
    while User.objects.filter(username=username).exists():
        username = f"{base}{i}"
        i += 1

    password_nueva = get_random_string(8)

    user = User.objects.create_user(username=username, password=password_nueva)

    # CREAR PERMISO

    permiso_urna, created = Permiso.objects.get_or_create(nombre='Urna')
    Permiso_Usuario.objects.create(usuario=user, permiso=permiso_urna)

    # CREAR PERSONA

    area_urna = Area.objects.filter(nombre=urna.area).first()

    persona = Persona.objects.create(
        nombre=nombre_urna,
        apellido=apellido_urna,
        genero=urna.genero,
        area=area_urna,
        usuario = user,
        clave_temporal=False
    )

    return user, password_nueva, persona

def crear_votos_urna(urna, persona):

    votantes = Persona.objects.filter(area=urna.area)

    if urna.genero != "U":
        votantes = votantes.filter(genero=urna.genero)

    votantes = votantes.exclude(id=persona.id)

    print(votantes.count())

    for v in votantes:

        print(v.nombre + " " + v.apellido)

        voto = Voto.objects.create(
            urna=urna,
            persona=v
        )

def crear_urnas_segunda_vuelta(segunda_vuelta, urnas):

    for u in urnas:

        nueva_urna = Urna.objects.create(
            elecciones=segunda_vuelta,
            area=u.area,
            genero=u.genero,
        )

        user, password_nueva, persona = crear_usuario_permiso_persona_urna(nueva_urna)

        nueva_urna.usuario = user

        nueva_urna.usuario.password = u.usuario.password

        user.save()
        nueva_urna.save()

        print("===========================================================================")
        print(f"Se creó la urna: Urna.{nueva_urna.area.nombre}.{nueva_urna.genero}.{nueva_urna.elecciones.periodo.anio}.P{nueva_urna.elecciones.periodo.periodo}.V{nueva_urna.elecciones.tipo}")
        
        votos_completos = u.votos_urna.filter(completo=True)

        crear_votos_urna_segunda_vuelta(nueva_urna, votos_completos)


def crear_votos_urna_segunda_vuelta(nueva_urna, votos_completos):

    print(f"Votos para segunda vuelta:{votos_completos.count()}")
    print("Padrón de segunda vuelta:")

    for v in votos_completos: 

        mismo_votante=v.persona

        print(v.persona)

        Voto.objects.create(
            urna=nueva_urna,
            persona=mismo_votante
        )






