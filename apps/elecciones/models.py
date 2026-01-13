from django.db import models, transaction
from django.contrib.auth.models import User  
from apps.usuarios.models import Persona, Area

class Periodo(models.Model):

    PERIODO = [
        ('1', 'P1'),
        ('2', 'P2'),
    ] 

    anio = models.SmallIntegerField()
    periodo = models.CharField(max_length=2, choices=PERIODO)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():  
            if self.activo:
                Periodo.objects.exclude(pk=self.pk).update(activo=False)
            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.anio} - {self.get_periodo_display()}'

class Elecciones(models.Model):

    TIPO = [
        ('1', 'V1'),
        ('2', 'V2'),
    ] 

    periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, null=True, blank=True, related_name='elecciones')
    tipo = models.CharField(max_length=2, choices=TIPO)
    activas = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        with transaction.atomic():  
            if self.activas:
                Elecciones.objects.exclude(pk=self.pk).update(activas=False)
            super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.periodo} | {"Primera Vuelta" if self.tipo == "1" else "Segunda Vuelta"}'


class Urna(models.Model):

    GENERO = [
        ('U', 'Unisex'),
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ] 

    elecciones = models.ForeignKey(Elecciones, on_delete=models.PROTECT, null=True, blank=True, related_name='urnas_elecciones')
    area = models.ForeignKey(Area, on_delete=models.PROTECT, null=True, blank=True, related_name='urnas_area')
    genero = models.CharField(max_length=1, choices=GENERO)
    usuario = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True, related_name='urna_usuario')

class Candidato_Jefe(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.PROTECT, null=True, blank=True, related_name='candidato_jefe_persona')
    elecciones = models.ForeignKey(Elecciones, on_delete=models.PROTECT, null=True, blank=True, related_name='candidato_jefe_elecciones')

class Candidato_Jefa(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.PROTECT, null=True, blank=True, related_name='candidato_jefa_persona')
    elecciones = models.ForeignKey(Elecciones, on_delete=models.PROTECT, null=True, blank=True, related_name='candidato_jefa_elecciones')

class Candidato_Materiales(models.Model):
    persona = models.ForeignKey(Persona, on_delete=models.PROTECT, null=True, blank=True, related_name='candidato_materiales_persona')
    elecciones = models.ForeignKey(Elecciones, on_delete=models.PROTECT, null=True, blank=True, related_name='candidato_materiales_elecciones')

class Voto(models.Model):
    urna = models.ForeignKey(Urna, on_delete=models.CASCADE, null=True, blank=True, related_name='votos_urna')
    persona = models.ForeignKey(Persona, on_delete=models.PROTECT, null=True, blank=True, related_name='votos_persona')
    permitido = models.BooleanField(default=False)
    completo = models.BooleanField(default=False)
    voto_jefe = models.ForeignKey(Candidato_Jefe, on_delete=models.PROTECT, null=True, blank=True, related_name='votos_jefe')
    voto_jefa = models.ForeignKey(Candidato_Jefa, on_delete=models.PROTECT, null=True, blank=True, related_name='votos_jefa')
    voto_materiales = models.ForeignKey(Candidato_Materiales, on_delete=models.PROTECT, null=True, blank=True, related_name='votos_materiales')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['urna', 'persona'], 
                name='voto_unico_por_persona_y_urna'
            )
        ]

