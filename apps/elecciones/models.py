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
    
    class Meta:
        verbose_name_plural = "Periodos"
        verbose_name = "Periodo"

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

    class Meta:
        verbose_name_plural = "Elecciones"
        verbose_name = "Elección"


class Urna(models.Model):

    GENERO = [
        ('U', 'Unisex'),
        ('M', 'Masculino'),
        ('F', 'Femenino'),
    ] 

    elecciones = models.ForeignKey(Elecciones, on_delete=models.CASCADE, null=True, blank=True, related_name='urnas_elecciones')
    area = models.ForeignKey(Area, on_delete=models.PROTECT, null=True, blank=True, related_name='urnas_area')
    genero = models.CharField(max_length=1, choices=GENERO)
    usuario = models.OneToOneField(User, on_delete=models.PROTECT, null=True, blank=True, related_name='urna_usuario')

    def __str__(self):
        return f"{self.usuario.username}"
    
    class Meta:
        verbose_name_plural = "Urnas"
        verbose_name = "Urna"


class Candidato(models.Model):

    TIPO = [
        ('JCM', 'Jefe de Campamento'),
        ('JCF', 'Jefa de Campamento'),
        ('JM', 'Jefe(a) de Materiales'),
    ] 

    persona = models.ForeignKey(Persona, on_delete=models.PROTECT, null=True, blank=True, related_name='candidato_persona')
    elecciones = models.ForeignKey(Elecciones, on_delete=models.CASCADE, null=True, blank=True, related_name='candidato_elecciones')
    tipo = models.CharField(max_length=3, choices=TIPO)

    def __str__(self):
        return f"{self.persona} fue candidato a {self.get_tipo_display()} en las {self.elecciones}"
    
    class Meta:
        verbose_name_plural = "Candidatos"
        verbose_name = "Candidato"

class Voto(models.Model): 
    urna = models.ForeignKey(Urna, on_delete=models.CASCADE, null=True, blank=True, related_name='votos_urna')
    persona = models.ForeignKey(Persona, on_delete=models.PROTECT, null=True, blank=True, related_name='votos_persona')
    permitido = models.BooleanField(default=False)
    completo = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.persona} {"votó" if self.completo else "votará"} en la urna {self.urna.usuario.username}"
    
    class Meta:
        verbose_name_plural = "Votos"
        verbose_name = "Voto"

class Sufragio(models.Model):
    elecciones = models.ForeignKey(Elecciones, on_delete=models.CASCADE, null=True, blank=True, related_name='sufragio_elecciones')
    voto_jefe = models.ForeignKey(Candidato, on_delete=models.CASCADE, null=True, blank=True, related_name='votos_jefe')
    voto_jefa = models.ForeignKey(Candidato, on_delete=models.CASCADE, null=True, blank=True, related_name='votos_jefa')
    voto_materiales = models.ForeignKey(Candidato, on_delete=models.CASCADE, null=True, blank=True, related_name='votos_materiales')

    def __str__(self):
        return f"Voto #{self.id} en {self.elecciones}"
    
    class Meta:
        verbose_name_plural = "Sufragios"
        verbose_name = "Sufragio"

class Se_Puede_Votar(models.Model):
    permitido = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        self.pk = 1  
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  
