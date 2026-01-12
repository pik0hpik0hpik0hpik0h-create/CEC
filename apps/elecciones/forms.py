from django import forms
from .models import Elecciones, Periodo

# CREAR PRIMERA VUELTA DE ELECCIONES
class form_crear_primera_vuelta(forms.ModelForm):

    class Meta:
        model = Elecciones
        fields = ['periodo']
    
    #PERIODO
    periodo = forms.ModelChoiceField(
        queryset=Periodo.objects.none(),   
        empty_label='Elija un periodo',
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