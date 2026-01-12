from django import forms
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm
from django.utils.translation import gettext_lazy as _
from datetime import date
from .models import Area, Persona

# INICIO DE SESIÓN
class form_login(AuthenticationForm):

    error_messages = {
        'invalid_login': _('El usuario o la contraseña no son correctos.'),
        'inactive': _('Esta cuenta se encuentra desactivada.'),
    }

    username = forms.CharField(
        error_messages={
        'required': 'Por favor, ingresa tu usuario.',
        }, 
        widget=forms.TextInput(attrs={
            'class': 'bg-stone-100 text-gray-500 rounded-lg text-xs font-montserrat font-medium input form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
            'placeholder': 'Usuario',
        })
    )

    password = forms.CharField(
        error_messages={
        'required': 'Por favor, ingresa tu contraseña.',
        }, 
        widget=forms.PasswordInput(attrs={
            'class': 'bg-stone-100 text-gray-500 rounded-lg text-xs font-montserrat font-medium input form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
            'placeholder': 'Contraseña',
        })
    )


























# EDICIÓN DE PERFIL
class form_editar_perfil(forms.ModelForm):

    class Meta:
        model = Persona
        fields = ['foto', 'fecha_nacimiento']

    foto = forms.ImageField(
        required=False,
        error_messages={
            'invalid': 'Archivo no válido.',
        },
        widget=forms.FileInput(attrs={
            'class': 'text-base-content/50 bg-neutral-content rounded-lg text-xs font-montserrat font-medium file-input file-input-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50 w-full',
            'accept': 'image/*',
        })
    )
 
    fecha_nacimiento = forms.DateField(
        input_formats=['%d-%m-%Y'],
        error_messages={
            'required': 'Por favor, ingrese una fecha de nacimiento.',
            'invalid': 'Formato inválido, use dd-mm-aaaa.',
        },
        widget=forms.TextInput(attrs={
            'class': 'bg-neutral-content rounded-lg text-xs font-montserrat font-medium input form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
            'placeholder': 'dd-mm-aaaa',
        })
    )

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')

        if fecha >= date.today():
            raise forms.ValidationError(
                'La fecha de nacimiento no puede ser posterior a hoy.'
            )

        return fecha

































# NUEVA CONTRASEÑA
class form_nueva_clave(SetPasswordForm):

    new_password1 = forms.CharField(
        error_messages={
        'required': 'Por favor, ingrese nueva contraseña.',
        },
        widget=forms.PasswordInput(attrs={
            'class': 'bg-stone-100 text-gray-500 rounded-lg text-xs font-montserrat font-medium input form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
            'placeholder': 'Nueva contraseña',
        })
    )

    new_password2 = forms.CharField(
        error_messages={
        'required': 'Por favor, confirme nueva contraseña.',
        },
        widget=forms.PasswordInput(attrs={
            'class': 'bg-stone-100 text-gray-500 rounded-lg text-xs font-montserrat font-medium input form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
            'placeholder': 'Confirmar contraseña',
        })
    )




























# REGISTRO DE USUARIO
class form_registrar_usuario(forms.ModelForm):

    class Meta:
        model = Persona
        fields = [
            'cedula',
            'nombre',
            'apellido',
            'genero',
            'fecha_nacimiento',
            'area',
        ]
    
    #CÉDULA
    cedula = forms.CharField(
        max_length=10,
        error_messages={
            'required': 'Por favor, ingrese un número de cédula.',
        }, 
        widget=forms.TextInput(attrs={
            'class': 'bg-neutral-content rounded-lg text-xs font-montserrat font-medium input form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
            'placeholder': 'Cedula',
            'inputmode': 'numeric',
            'pattern': '[0-9]*',  
        })
    )

    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if not cedula.isdigit():
            raise forms.ValidationError('La cédula solo debe contener números.')
        if len(cedula) != 10:
            raise forms.ValidationError('La cédula debe tener exactamente 10 dígitos.')
        return cedula
    
    #NOMBRE
    nombre = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Por favor, ingrese un nombre.',
        }, 
        widget=forms.TextInput(attrs={
            'class': 'bg-neutral-content rounded-lg text-xs font-montserrat font-medium input form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
            'placeholder': 'Nombre', 
        })
    )

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if not nombre.replace(' ', '').isalpha():
            raise forms.ValidationError(
                'El nombre solo debe contener letras y espacios.'
            )
        return nombre
    
    #APELLIDO
    apellido = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Por favor, ingrese un apellido.',
        }, 
        widget=forms.TextInput(attrs={
            'class': 'bg-neutral-content rounded-lg text-xs font-montserrat font-medium input form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
            'placeholder': 'Apellido', 
        })
    )

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido')
        if not apellido.replace(' ', '').isalpha():
            raise forms.ValidationError(
                'El apellido solo debe contener letras y espacios.'
            )
        return apellido
    
    #GÉNERO
    genero = forms.ChoiceField(
        choices=(
            ('M', 'Masculino'),
            ('F', 'Femenino'),
        ),
        widget=forms.RadioSelect(attrs={
            'class': 'radio radio-accent radio-xs'
        }),
        error_messages={
            'required': 'Por favor, seleccione un género.',
        }
    )

    #FECHA DE NACIMIENTO
    fecha_nacimiento = forms.DateField(
        input_formats=['%d-%m-%Y'],
        error_messages={
            'required': 'Por favor, ingrese una fecha de nacimiento.',
            'invalid': 'Formato inválido, use dd-mm-aaaa.',
        },
        widget=forms.TextInput(attrs={
            'class': 'bg-neutral-content rounded-lg text-xs font-montserrat font-medium input form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
            'placeholder': 'dd-mm-aaaa',
        })
    )

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')

        if fecha >= date.today():
            raise forms.ValidationError(
                'La fecha de nacimiento no puede ser posterior a hoy.'
            )

        return fecha
    
    #ÁREA
    area = forms.ModelChoiceField(
        queryset=Area.objects.none(),   
        empty_label='Elija un área',
        error_messages={
            'required': 'Por favor, seleccione un área.',
        },
        widget=forms.Select(attrs={
            'class': 'custom-select bg-neutral-content rounded-lg text-xs font-montserrat font-medium select form-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50',
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['area'].queryset = Area.objects.all()












    





















class form_registrar_usuario_csv(forms.Form):

    archivo = forms.FileField(
        label='Archivo CSV',
        error_messages={
            'required': 'Por favor, seleccione un archivo CSV.',
            'invalid': 'Archivo no válido.',
        },
        widget=forms.ClearableFileInput(attrs={
            'class': 'text-base-content/50 bg-neutral-content rounded-lg text-xs font-montserrat font-medium file-input file-input-accent mt-2 border-0 focus:outline-none focus:ring-1 focus:ring-accent/50 w-full',
            'accept': '.csv',
        })
    )