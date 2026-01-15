from django import forms
from apps.usuarios.models import Area, Persona
from .models import Elecciones, Periodo, Urna, Candidato

# CREAR PRIMERA VUELTA DE ELECCIONES
class form_crear_primera_vuelta(forms.ModelForm):

    class Meta:
        model = Elecciones
        fields = ['periodo']
    
    #PERIODO
    periodo = forms.ModelChoiceField(
        queryset=Periodo.objects.filter(activo=True),   
        initial=Periodo.objects.filter(activo=True).first(), 
        empty_label=None,
        error_messages={
            'required': 'Por favor, seleccione un periodo.',
        },
        widget=forms.Select(attrs={
            'class': 'custom-select bg-neutral-content rounded-lg text-xs font-montserrat font-medium select form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['periodo'].queryset = Periodo.objects.filter(activo=True)

# CREAR URNAS 
class form_crear_urna(forms.ModelForm):

    class Meta:
        model = Urna
        fields = ['elecciones', 'area', 'genero']
    
    #ELECCIONES
    elecciones = forms.ModelChoiceField(
        queryset=Elecciones.objects.filter(activas=True),   
        initial=Elecciones.objects.filter(activas=True).first(),
        empty_label=None,

        error_messages={
            'required': 'Por favor, seleccione unas elecciones.',
        },
        widget=forms.Select(attrs={
            'class': 'custom-select bg-neutral-content rounded-lg text-xs font-montserrat font-medium select form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
        })
    )

    #AREA
    area = forms.ModelChoiceField(
        queryset=Area.objects.all(),   
        empty_label='Elija un área',

        error_messages={
            'required': 'Por favor, seleccione un área.',
        },
        widget=forms.Select(attrs={
            'class': 'custom-select bg-neutral-content rounded-lg text-xs font-montserrat font-medium select form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
        })
    )

    #GÉNERO
    genero = forms.ChoiceField(
        choices=(
            ('U', 'Unisex'),
            ('M', 'Masculino'),
            ('F', 'Femenino'),
        ),
        widget=forms.Select(attrs={
            'class': 'custom-select bg-neutral-content rounded-lg text-xs font-montserrat font-medium select form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
        }),
        error_messages={
            'required': 'Por favor, seleccione un género.',
        }
    )

# REGISTRAR CANDIDATOS
class form_registrar_candidato(forms.Form):
    
    #ELECCIONES
    elecciones = forms.ModelChoiceField(
        queryset=Elecciones.objects.filter(activas=True),   
        initial=Elecciones.objects.filter(activas=True).first(),
        empty_label=None,

        error_messages={
            'required': 'Por favor, seleccione unas elecciones.',
        },
        widget=forms.Select(attrs={
            'class': 'custom-select bg-neutral-content rounded-lg text-xs font-montserrat font-medium select form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
        })
    )

    #PERSONA
    persona = forms.ModelMultipleChoiceField(
        queryset=Persona.objects.filter(area__nombre__in=['Roja', 'Amarilla']).exclude(cedula=None),
        required=True,

        error_messages={
            'required': 'Por favor, seleccione al menos una persona.',
        },

        widget=forms.SelectMultiple(attrs={
            'class': 'custom-select bg-neutral-content rounded-lg text-xs font-montserrat font-medium select form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
        })
    )

    #TIPO
    tipo = forms.ChoiceField(
        choices=(
            ('', 'Elija un cargo'),
            ('JCM', 'Jefe de Campamento'),
            ('JCF', 'Jefa de Campamento'),
            ('JM', 'Jefe(a) de Materiales'),
        ),
        required=True,
        widget=forms.Select(attrs={
            'class': 'custom-select bg-neutral-content rounded-lg text-xs font-montserrat font-medium select form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
        }),
        error_messages={
            'required': 'Por favor, seleccione un cargo.',
        }
    )

# VER RESULTADOS
class form_consultar_resultados(forms.Form):
    
    #ELECCIONES
    elecciones = forms.ModelChoiceField(
        queryset=Elecciones.objects.none(),
        empty_label=None,
        error_messages={
            'required': 'Por favor, seleccione unas elecciones.',
        },
        widget=forms.Select(attrs={
            'class': 'custom-select bg-neutral-content rounded-lg text-xs font-montserrat font-medium select form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['elecciones'].queryset = Elecciones.objects.all()
        self.fields['elecciones'].initial = Elecciones.objects.filter(activas=True).first()

