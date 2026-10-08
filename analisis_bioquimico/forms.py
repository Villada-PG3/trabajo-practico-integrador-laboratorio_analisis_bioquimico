from django import forms
from datetime import date, timedelta
from .models import Paciente, Medico, Estudio


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