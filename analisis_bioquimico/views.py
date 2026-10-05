from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Paciente, SolicitudAnalisis, SolicitudEstudio, Resultado, RangoReferencia, Comprobante

# ==========================================
# SECCIÓN: PORTAL DE PACIENTES (INTEGRANTE 3)
# ==========================================

def login_paciente(request):
    """
    Pantalla de acceso para el paciente usando únicamente DNI y CAP.
    """
    if request.method == 'POST':
        dni = request.POST.get('dni', '').strip()
        cap = request.POST.get('cap', '').strip()

        if not dni or not cap:
            messages.error(request, 'Por favor ingrese su DNI y su Clave de Acceso Personal (CAP).')
            return render(request, 'analisis_bioquimico/portal/login.html')

        # Buscamos si existe un paciente con ese DNI
        try:
            paciente = Paciente.objects.get(dni=dni)
        except Paciente.DoesNotExist:
            messages.error(request, 'No se encontró ningún paciente registrado con ese DNI.')
            return render(request, 'analisis_bioquimico/portal/login.html')

        # Verificamos si la CAP coincide con el Paciente (campo cap) o con algún Comprobante expedido
        comprobante_valido = Comprobante.objects.filter(solicitud__paciente=paciente, cap=cap).exists()
        cap_paciente_valida = (paciente.cap == cap)

        if comprobante_valido or cap_paciente_valida:
            # Guardamos los datos clave en la sesión del usuario
            request.session['paciente_id'] = paciente.id
            request.session['paciente_nombre'] = f"{paciente.nombre} {paciente.apellido}"
            
            # CORRECCIÓN: Agregar el namespace 'analisis_bioquimico:'
            return redirect('analisis_bioquimico:portal_historial')
        else:
            messages.error(request, 'La Clave de Acceso Personal (CAP) ingresada no es válida para este DNI.')

    return render(request, 'analisis_bioquimico/portal/login.html')


def logout_paciente(request):
    """
    Cierra la sesión activa del paciente y lo devuelve al login.
    """
    request.session.flush()
    # CORRECCIÓN: Agregar el namespace 'analisis_bioquimico:'
    return redirect('analisis_bioquimico:login_paciente')


def historial_solicitudes(request):
    """
    Muestra el listado de solicitudes del paciente autenticado y el detalle del resultado seleccionado.
    """
    paciente_id = request.session.get('paciente_id')
    if not paciente_id:
        messages.warning(request, 'Debe ingresar con su DNI y CAP para consultar sus resultados.')
        # CORRECCIÓN: Agregar el namespace 'analisis_bioquimico:'
        return redirect('analisis_bioquimico:login_paciente')

    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    # Consulta de solicitudes asociadas al paciente
    solicitudes = SolicitudAnalisis.objects.filter(paciente=paciente).select_related(
        'estado', 'receta__medico'
    ).order_by('-fecha_hora')

    # Solicitud seleccionada por parámetro GET (?solicitud_id=X)
    solicitud_id_seleccionada = request.GET.get('solicitud_id')
    solicitud_seleccionada = None
    resultados_detalle = []

    if solicitud_id_seleccionada:
        solicitud_seleccionada = get_object_or_404(SolicitudAnalisis, id=solicitud_id_seleccionada, paciente=paciente)
        
        # Obtenemos los estudios y sus correspondientes valores hallados
        estudios_solicitud = SolicitudEstudio.objects.filter(solicitud=solicitud_seleccionada).select_related('estudio')
        
        for sol_estudio in estudios_solicitud:
            resultado = Resultado.objects.filter(solicitud_estudio=sol_estudio).first()
            rangos = RangoReferencia.objects.filter(estudio=sol_estudio.estudio)
            
            resultados_detalle.append({
                'solicitud_estudio': sol_estudio,
                'estudio': sol_estudio.estudio,
                'resultado': resultado,
                'rangos': rangos,
            })

    context = {
        'paciente': paciente,
        'solicitudes': solicitudes,
        'solicitud_seleccionada': solicitud_seleccionada,
        'resultados_detalle': resultados_detalle,
    }
    return render(request, 'analisis_bioquimico/portal/historial.html', context)


# ==========================================
# SECCIÓN: INSTITUCIONAL / LANDING PAGE
# ==========================================

def home(request):
    """
    Landing Page pública inspirada en Laboratorio LACE.
    """
    return render(request, 'analisis_bioquimico/home.html')