from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _

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

# REGISTRO DE USUARIO
class form_registrar_usuario(forms.Form):

    cedula = forms.CharField(
        max_length=10,
        error_messages={
            'required': 'Por favor, ingresa un número de cédula.',
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
    
    nombre = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Por favor, ingresa un nombre.',
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
    
    apellido = forms.CharField(
        max_length=255,
        error_messages={
            'required': 'Por favor, ingresa un apellido.',
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
    
    genero = forms.ChoiceField(
        choices=(
            ('M', 'Masculino'),
            ('F', 'Femenino'),
        ),
        widget=forms.RadioSelect(attrs={
            'class': 'radio radio-accent radio-xs'
        }),
        error_messages={
            'required': 'Por favor, selecciona un género.',
        }
    )

    


