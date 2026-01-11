from django.db import models
from django.contrib.auth.models import User  
from cloudinary.models import CloudinaryField

class Area(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Persona(models.Model):

    GENERO = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ] 

    cedula = models.CharField(max_length=10, unique=True, blank=True, default='')
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    genero = models.CharField(max_length=1, choices=GENERO)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    foto = CloudinaryField('foto', default='DEFAULT_PROFILE_PIC_aszqw2', folder='cec/perfiles')
    area = models.ForeignKey(Area, on_delete=models.PROTECT, null=True, blank=True, related_name='personas')
    usuario = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True, related_name='persona')
    clave_temporal = models.BooleanField(default=True)

class Permiso(models.Model):
    nombre = models.CharField(max_length=255)

class Permiso_Usuario(models.Model):
    permiso = models.ForeignKey(Permiso, on_delete=models.PROTECT)
    usuario = models.ForeignKey(User, on_delete=models.PROTECT)


    
