from django import forms
from captcha.fields import CaptchaField
from .models import Contacto
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class ContactoForm(forms.ModelForm):
    # Se agrega el campo captcha al formulario
    captcha = CaptchaField()

    class Meta:
        model = Contacto
        # Nota: 'captcha' no se incluye en 'fields' porque no está en el modelo.
        fields = ['nombre', 'email', 'mensaje']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'id': 'name',
                'required': 'required',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Email',
                'id': 'email',
                'required': 'required',
            }),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Message',
                'rows': 8,
                'required': 'required',
            }),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if len(nombre) < 3:
            raise ValidationError(_("El nombre debe tener más de 3 caracteres"))
        return nombre

    def clean_mensaje(self):
        mensaje = self.cleaned_data['mensaje']
        num_palabras = len(mensaje.split())
        if num_palabras < 4:
            raise ValidationError(_("El mensaje debe tener más de 4 palabras"))
        return mensaje
