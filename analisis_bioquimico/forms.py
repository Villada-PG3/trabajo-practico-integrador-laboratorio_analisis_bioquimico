from django import forms
from datetime import date, timedelta
from .models import Paciente, Medico, Estudio, RangoReferencia


class CrearSolicitudForm(forms.Form):
    paciente = forms.ModelChoiceField(
        queryset=Paciente.objects.all(),
        label="Paciente",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleccione un Paciente --"
    )
    medico = forms.ModelChoiceField(
        queryset=Medico.objects.filter(validado_colegio=True),
        label="Médico Solicitante (con MP Habilitada)",
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="-- Seleccione un Médico --"
    )
    fecha_emision = forms.DateField(
        label="Fecha de la Receta",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    archivo_pdf = forms.FileField(
        label="Receta Escaneada (PDF / Imagen)",
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,image/*'})
    )
    estudios = forms.ModelMultipleChoiceField(
        queryset=Estudio.objects.all(),
        label="Estudios Indicados en la Receta",
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )

    def clean_fecha_emision(self):
        fecha_emision = self.cleaned_data.get('fecha_emision')
        if fecha_emision:
            hoy = date.today()
            
            # Validar que no sea una fecha futura
            if fecha_emision > hoy:
                raise forms.ValidationError("La fecha de la receta no puede ser posterior al día de hoy.")

            # Validar que no supere 1 mes (30 días) de antigüedad
            limite_antiguedad = hoy - timedelta(days=30)
            if fecha_emision < limite_antiguedad:
                raise forms.ValidationError(
                    "La receta no puede tener más de 1 mes (30 días) de antigüedad al momento de cargarla."
                )

        return fecha_emision
    
class EstudioForm(forms.ModelForm):
    class Meta:
        model = Estudio
        fields = [
            'codigo',
            'nombre',
            'descripcion',
            'metodo_tecnica',
            'unidad_medida',
        ]

        widgets = {
            'codigo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 412'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Glucemia'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
            'metodo_tecnica': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Enzimático - Autoanalizador'
            }),
            'unidad_medida': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: mg/dL'
            }),
        }


class RangoReferenciaForm(forms.ModelForm):
    class Meta:
        model = RangoReferencia
        fields = [
            'valor_min',
            'valor_max',
            'genero',
            'edad_min',
            'edad_max',
        ]

        widgets = {
            'valor_min': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any'
            }),
            'valor_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': 'any'
            }),
            'genero': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'edad_min': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'edad_max': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()

        valor_min = cleaned_data.get('valor_min')
        valor_max = cleaned_data.get('valor_max')
        edad_min = cleaned_data.get('edad_min')
        edad_max = cleaned_data.get('edad_max')

        if (
            valor_min is not None
            and valor_max is not None
            and valor_min > valor_max
        ):
            raise forms.ValidationError(
                'El valor mínimo no puede ser mayor que el valor máximo.'
            )

        if (
            edad_min is not None
            and edad_max is not None
            and edad_min > edad_max
        ):
            raise forms.ValidationError(
                'La edad mínima no puede ser mayor que la edad máxima.'
            )

        return cleaned_data