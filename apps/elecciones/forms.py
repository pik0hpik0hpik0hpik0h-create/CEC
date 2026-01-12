from django import forms
from apps.usuarios.models import Area
from .models import Elecciones, Periodo, Urna

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
