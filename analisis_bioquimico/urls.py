from django.urls import path
from . import views

app_name = "analisis_bioquimico"

urlpatterns = [
    path("", views.home, name="home"),
    
    # Rutas del Módulo 1 (Recepción, Pacientes y Médicos)
    path('recepcion/solicitud/nueva/', views.recepcion_crear_solicitud, name='recepcion_crear_solicitud'),
    
    # Rutas del Módulo 3 (Portal del Paciente)
    path('portal/login/', views.login_paciente, name='login_paciente'),
    path('portal/logout/', views.logout_paciente, name='logout_paciente'),
    path('portal/historial/', views.historial_solicitudes, name='portal_historial'),
    path('recepcion/pacientes/', views.login_paciente, name='login'),
    # Rutas del Módulo 2 (Extracción y Laboratorio)
path(
    'laboratorio/estudios/',
    views.estudios_lista,
    name='estudios_lista'
),

path(
    'laboratorio/estudios/nuevo/',
    views.estudio_crear,
    name='estudio_crear'
),

path(
    'laboratorio/estudios/<int:estudio_id>/editar/',
    views.estudio_editar,
    name='estudio_editar'
),

path(
    'laboratorio/estudios/<int:estudio_id>/eliminar/',
    views.estudio_eliminar,
    name='estudio_eliminar'
),

path(
    'laboratorio/estudios/<int:estudio_id>/rangos/',
    views.estudio_rangos,
    name='estudio_rangos'
),

path(
    'laboratorio/rangos/<int:rango_id>/eliminar/',
    views.rango_eliminar,
    name='rango_eliminar'
),
]
]

