from django.urls import path
from . import views


app_name = "analisis_bioquimico"


urlpatterns = [

    # ==========================================
    # HOME
    # ==========================================

    path(
        "",
        views.home,
        name="home"
    ),


    # ==========================================
    # ACCESO / PORTAL DEL PACIENTE
    # ==========================================

    path(
        'recepcion/pacientes/',
        views.login_paciente,
        name='login'
    ),

    path(
        'portal/login/',
        views.login_paciente,
        name='login_paciente'
    ),

    path(
        'portal/logout/',
        views.logout_paciente,
        name='logout_paciente'
    ),

    path(
        'portal/historial/',
        views.historial_solicitudes,
        name='portal_historial'
    ),

    path(
        'portal/solicitud/<int:solicitud_id>/resultado/',
        views.detalle_pdf_resultados,
        name='detalle_pdf_resultados'
    ),


    # ==========================================
    # LOGIN / PANELES DE PERSONAL
    # ==========================================

    path(
        'personal/login/',
        views.login_personal,
        name='login_personal'
    ),

    path(
        'personal/logout/',
        views.logout_personal,
        name='logout_personal'
    ),

    path(
        'personal/recepcion/',
        views.panel_recepcion,
        name='panel_recepcion'
    ),

    path(
        'personal/extraccion/',
        views.panel_extraccion,
        name='panel_extraccion'
    ),

    path(
        'personal/extraccion/<int:solicitud_id>/registrar/',
        views.registrar_extraccion,
        name='registrar_extraccion'
    ),

    path(
        'personal/extraccion/comprobante/<int:comprobante_id>/',
        views.comprobante_extraccion,
        name='comprobante_extraccion'
    ),

    path(
        'personal/laboratorio/',
        views.panel_laboratorio,
        name='panel_laboratorio'
    ),

    path(
        'personal/laboratorio/reportes/',
        views.reportes_laboratorio,
        name='reportes_laboratorio'
    ),


    # ==========================================
    # MÓDULO 1 - RECEPCIÓN
    # ==========================================

    path(
        'recepcion/solicitud/nueva/',
        views.recepcion_crear_solicitud,
        name='recepcion_crear_solicitud'
    ),
    path(
        'recepcion/pacientes/gestion/',
        views.gestion_pacientes,
        name='gestion_pacientes'
    ),
    # ==========================================
    # SALA DE ESPERA
    # ==========================================

    path(
        'sala-espera/',
        views.sala_espera,
        name='sala_espera'
    ),

    path(
        'sala-espera/datos/',
        views.sala_espera_datos,
        name='sala_espera_datos'
    ),

    path(
        'personal/extraccion/<int:solicitud_id>/llamar/',
        views.llamar_paciente,
        name='llamar_paciente'
    ),
    # ==========================================
    # MÓDULO 2 - GESTIÓN DE ESTUDIOS
    # ==========================================

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


    # ==========================================
    # RESPONSABLE DE ANÁLISIS
    # ==========================================

    path(
        'panel-bioquimico/',
        views.panel_bioquimico,
        name='panel_bioquimico'
    ),

    path(
        'cargar-resultados/<int:solicitud_id>/',
        views.cargar_resultados,
        name='cargar_resultados'
    ),
    path(
        'recepcion/medicos/',
        views.gestion_medicos,
        name='gestion_medicos'
    ),

    path(
        'colegio-medico/api/validar/',
        views.api_validar_matricula,
        name='api_validar_matricula'
    ),
]