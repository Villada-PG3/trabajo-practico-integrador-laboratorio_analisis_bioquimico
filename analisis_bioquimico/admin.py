from django.contrib import admin
from .models import (
    Paciente,
    Medico,
    Recepcionista,
    Extraccionista,
    ResponsableAnalisis,
    EstadoSolicitud,
    Estudio,
    RangoReferencia,
    Receta,
    SolicitudAnalisis,
    SolicitudEstudio,
    Muestra,
    Resultado,
    Comprobante,
    Notificacion,
)


class PacienteAdmin(admin.ModelAdmin):
    list_display= ("id", "apellido","nombre","dni","telefono","email")
    search_fields= ("apellido","nombre","dni")
# Register your models here.

class MedicoAdmin(admin.ModelAdmin):
    list_display = ('id', 'apellido', 'nombre', 'matricula', 'especialidad', 'validado_colegio')
    search_fields = ('apellido', 'nombre', 'matricula')
    list_filter = ('validado_colegio', 'especialidad')

class RecepcionistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'apellido', 'nombre', 'email')
    search_fields = ('apellido', 'nombre')

class ExtraccionistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'apellido', 'nombre', 'legajo')
    search_fields = ('apellido', 'nombre', 'legajo')

class ResponsableAnalisisAdmin(admin.ModelAdmin):
    list_display = ('id', 'apellido', 'nombre', 'legajo', 'cargo')
    search_fields = ('apellido', 'nombre', 'legajo')

class EstadoSolicitudAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')

class EstudioAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre', 'metodo_tecnica', 'unidad_medida')
    search_fields = ('codigo', 'nombre')

class RangoReferenciaAdmin(admin.ModelAdmin):
    list_display = ('id', 'estudio', 'valor_min', 'valor_max', 'genero', 'edad_min', 'edad_max')
    list_filter = ('estudio', 'genero')

class RecetaAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'medico', 'fecha_emision')
    list_filter = ('fecha_emision',)
    search_fields = ('paciente__apellido', 'paciente__dni', 'medico__apellido')

class SolicitudAnalisisAdmin(admin.ModelAdmin):
    list_display = ('id', 'paciente', 'recepcionista', 'estado', 'fecha_hora')
    list_filter = ('estado', 'fecha_hora')
    search_fields = ('paciente__apellido', 'paciente__dni')

class SolicitudEstudioAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'estudio', 'estado')
    list_filter = ('estado', 'estudio')

class MuestraAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'tipo', 'extraccionista', 'fecha_hora_extraccion')
    list_filter = ('tipo', 'fecha_hora_extraccion')

class ResultadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud_estudio', 'valor_hallado', 'responsable', 'fecha_registro')
    list_filter = ('fecha_registro', 'responsable')

class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'numero_paciente', 'fecha_emision', 'cap')

class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'solicitud', 'tipo', 'estado', 'fecha_envio')
    list_filter = ('tipo', 'estado')

admin.site.register(Paciente,PacienteAdmin)
admin.site.register(Medico,MedicoAdmin)
admin.site.register(Recepcionista,RecepcionistaAdmin)
admin.site.register(Extraccionista,ExtraccionistaAdmin)
admin.site.register(ResponsableAnalisis,ResponsableAnalisisAdmin)
admin.site.register(EstadoSolicitud,EstadoSolicitudAdmin)
admin.site.register(Estudio,EstudioAdmin)
admin.site.register(RangoReferencia,RangoReferenciaAdmin)
admin.site.register(Receta,RecetaAdmin)
admin.site.register(SolicitudAnalisis,SolicitudAnalisisAdmin)
admin.site.register(SolicitudEstudio,SolicitudEstudioAdmin)
admin.site.register(Muestra,MuestraAdmin)
admin.site.register(Resultado,ResultadoAdmin)
admin.site.register(Comprobante,ComprobanteAdmin)
admin.site.register(Notificacion,NotificacionAdmin)

