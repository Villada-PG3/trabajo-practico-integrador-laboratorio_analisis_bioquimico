from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from .models import (
    Paciente, Medico, Recepcionista, EstadoSolicitud, 
    Receta, SolicitudAnalisis, SolicitudEstudio, Resultado, 
    RangoReferencia, Comprobante
)
from .forms import CrearSolicitudForm


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

        try:
            paciente = Paciente.objects.get(dni=dni)
        except Paciente.DoesNotExist:
            messages.error(request, 'No se encontró ningún paciente registrado con ese DNI.')
            return render(request, 'analisis_bioquimico/portal/login.html')

        comprobante_valido = Comprobante.objects.filter(solicitud__paciente=paciente, cap=cap).exists()
        cap_paciente_valida = (paciente.cap == cap)

        if comprobante_valido or cap_paciente_valida:
            request.session['paciente_id'] = paciente.id
            request.session['paciente_nombre'] = f"{paciente.nombre} {paciente.apellido}"
            return redirect('analisis_bioquimico:portal_historial')
        else:
            messages.error(request, 'La Clave de Acceso Personal (CAP) ingresada no es válida para este DNI.')

    return render(request, 'analisis_bioquimico/portal/login.html')


def logout_paciente(request):
    """
    Cierra la sesión activa del paciente y lo devuelve al login.
    """
    request.session.flush()
    return redirect('analisis_bioquimico:login_paciente')


def historial_solicitudes(request):
    """
    Muestra el listado de solicitudes del paciente autenticado y el detalle del resultado seleccionado.
    """
    paciente_id = request.session.get('paciente_id')
    if not paciente_id:
        messages.warning(request, 'Debe ingresar con su DNI y CAP para consultar sus resultados.')
        return redirect('analisis_bioquimico:login_paciente')

    paciente = get_object_or_404(Paciente, id=paciente_id)
    
    solicitudes = SolicitudAnalisis.objects.filter(paciente=paciente).select_related(
        'estado', 'receta__medico'
    ).order_by('-fecha_hora')

    solicitud_id_seleccionada = request.GET.get('solicitud_id')
    solicitud_seleccionada = None
    resultados_detalle = []

    if solicitud_id_seleccionada:
        solicitud_seleccionada = get_object_or_404(SolicitudAnalisis, id=solicitud_id_seleccionada, paciente=paciente)
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
    return render(request, 'analisis_bioquimico/home.html')


def login_unificado(request):
    """
    Vista de login centralizada con pestañas para Pacientes y Recepción.
    """
    if request.method == 'POST':
        tipo_login = request.POST.get('tipo_login')

        if tipo_login == 'paciente':
            dni = request.POST.get('dni', '').strip()
            cap = request.POST.get('cap', '').strip()

            paciente = Paciente.objects.filter(dni=dni, cap=cap).first()
            if paciente:
                request.session['paciente_id'] = paciente.id
                request.session['paciente_nombre'] = f"{paciente.nombre} {paciente.apellido}"
                messages.success(request, f"¡Bienvenido/a, {paciente.nombre}!")
                return redirect('analisis_bioquimico:portal_historial')
            else:
                messages.error(request, 'DNI o CAP incorrectos. Verifique los datos ingresados.')

        elif tipo_login == 'recepcion':
            usuario = request.POST.get('usuario', '').strip()
            clave = request.POST.get('clave', '').strip()

            if usuario == 'recepcion' and clave == '1234':
                request.session['recepcionista_id'] = 1
                messages.success(request, 'Sesión de Recepción iniciada correctamente.')
                return redirect('analisis_bioquimico:recepcion_crear_solicitud')
            else:
                messages.error(request, 'Usuario o contraseña de Recepción inválidos.')

    return render(request, 'analisis_bioquimico/login.html')


# ==========================================
# SECCIÓN: MÓDULO 1 - RECEPCCIÓN DE RECETA
# ==========================================

def recepcion_crear_solicitud(request):
    """
    Formulario para la recepción de receta y creación de la solicitud inicial.
    Valida la antigüedad de la receta y procesa el archivo escaneado.
    """
    initial_data = {}
    if 'paciente_id' in request.GET:
        initial_data['paciente'] = request.GET.get('paciente_id')
    if 'medico_id' in request.GET:
        initial_data['medico'] = request.GET.get('medico_id')

    if request.method == 'POST':
        form = CrearSolicitudForm(request.POST, request.FILES)
        if form.is_valid():
            paciente = form.cleaned_data['paciente']
            medico = form.cleaned_data['medico']
            fecha_emision = form.cleaned_data['fecha_emision']
            archivo_pdf = form.cleaned_data['archivo_pdf']
            estudios_seleccionados = form.cleaned_data['estudios']

            # 1. Registrar la Receta escaneada
            receta = Receta.objects.create(
                paciente=paciente,
                medico=medico,
                fecha_emision=fecha_emision,
                archivo_pdf=archivo_pdf
            )

            # 2. Obtener o crear Estado inicial
            estado_pendiente, _ = EstadoSolicitud.objects.get_or_create(
                nombre='Pendiente de muestra',
                defaults={'descripcion': 'Solicitud ingresada en recepción.'}
            )

            # 3. Obtener recepcionista de turno
            recepcionista = Recepcionista.objects.first()
            if not recepcionista:
                recepcionista = Recepcionista.objects.create(
                    nombre="Mesa de", apellido="Entrada", email="recepcion@laboratoriosac.com.ar"
                )

            # 4. Crear la Solicitud de Análisis
            solicitud = SolicitudAnalisis.objects.create(
                paciente=paciente,
                receta=receta,
                recepcionista=recepcionista,
                estado=estado_pendiente
            )

            # 5. Asociar los Estudios seleccionados
            for estudio in estudios_seleccionados:
                SolicitudEstudio.objects.create(
                    solicitud=solicitud,
                    estudio=estudio,
                    estado='Pendiente'
                )

            # 6. Notificación opcional por email al paciente
            if paciente.email:
                asunto = f"Laboratorio AC - Confirmación de Solicitud #{solicitud.id}"
                estudios_texto = "\n".join([f"- {e.codigo}: {e.nombre}" for e in estudios_seleccionados])
                mensaje = (
                    f"Hola {paciente.nombre} {paciente.apellido},\n\n"
                    f"Se ha registrado exitosamente tu solicitud #{solicitud.id}.\n\n"
                    f"Estudios:\n{estudios_texto}\n\n"
                    f"Aguarde en la sala de espera.\n\n"
                    f"Atentamente,\nLaboratorio AC"
                )
                try:
                    send_mail(asunto, mensaje, 'no-reply@laboratoriosac.com.ar', [paciente.email], fail_silently=True)
                except Exception:
                    pass

            messages.success(
                request, 
                f"Solicitud #{solicitud.id} cargada exitosamente con su receta escaneada para {paciente.nombre} {paciente.apellido}."
            )
            return redirect('analisis_bioquimico:recepcion_crear_solicitud')
    else:
        form = CrearSolicitudForm(initial=initial_data)

    return render(request, 'analisis_bioquimico/recepcion/crear_solicitud.html', {'form': form})