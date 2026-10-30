from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.db import transaction
from django.views.decorators.http import require_http_methods
from decimal import Decimal, InvalidOperation

from .models import (
    Paciente,
    Medico,
    Recepcionista,
    EstadoSolicitud,
    Estudio,
    Receta,
    SolicitudAnalisis,
    SolicitudEstudio,
    Resultado,
    RangoReferencia,
    Comprobante,
    Muestra,
    Extraccionista,
)

from .forms import (
    CrearSolicitudForm,
    EstudioForm,
    RangoReferenciaForm,
)

from .services import enviar_email_finalizacion

# ==========================================
# SECCIÓN: PORTAL DE PACIENTES
# ==========================================

def login_paciente(request):
    """
    Pantalla de acceso para pacientes usando DNI y CAP.
    También funciona como pantalla unificada de acceso,
    ya que desde el template se puede ingresar como Personal.
    """

    if request.method == 'POST':
        dni = request.POST.get('dni', '').strip()
        cap = request.POST.get('cap', '').strip()

        if not dni or not cap:
            messages.error(
                request,
                'Por favor ingrese su DNI y su Clave de Acceso Personal (CAP).'
            )
            return render(
                request,
                'analisis_bioquimico/portal/login.html'
            )

        try:
            paciente = Paciente.objects.get(dni=dni)

        except Paciente.DoesNotExist:
            messages.error(
                request,
                'No se encontró ningún paciente registrado con ese DNI.'
            )

            return render(
                request,
                'analisis_bioquimico/portal/login.html'
            )

        comprobante_valido = Comprobante.objects.filter(
            solicitud__paciente=paciente,
            cap=cap
        ).exists()

        cap_paciente_valida = paciente.cap == cap

        if comprobante_valido or cap_paciente_valida:

            request.session['paciente_id'] = paciente.id
            request.session['paciente_nombre'] = (
                f"{paciente.nombre} {paciente.apellido}"
            )

            return redirect(
                'analisis_bioquimico:portal_historial'
            )

        messages.error(
            request,
            'La Clave de Acceso Personal (CAP) ingresada no es válida para este DNI.'
        )

    return render(
        request,
        'analisis_bioquimico/portal/login.html'
    )


def logout_paciente(request):
    """
    Cierra la sesión activa del paciente.
    """

    request.session.flush()

    return redirect(
        'analisis_bioquimico:login'
    )


def historial_solicitudes(request):
    """
    Muestra las solicitudes del paciente autenticado
    y sus resultados.
    """

    paciente_id = request.session.get('paciente_id')

    if not paciente_id:
        messages.warning(
            request,
            'Debe ingresar con su DNI y CAP para consultar sus resultados.'
        )

        return redirect(
            'analisis_bioquimico:login'
        )

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    solicitudes = SolicitudAnalisis.objects.filter(
        paciente=paciente
    ).select_related(
        'estado',
        'receta__medico'
    ).order_by(
        '-fecha_hora'
    )

    solicitud_id_seleccionada = request.GET.get(
        'solicitud_id'
    )

    solicitud_seleccionada = None
    resultados_detalle = []

    if solicitud_id_seleccionada:

        solicitud_seleccionada = get_object_or_404(
            SolicitudAnalisis,
            id=solicitud_id_seleccionada,
            paciente=paciente
        )

        estudios_solicitud = SolicitudEstudio.objects.filter(
            solicitud=solicitud_seleccionada
        ).select_related(
            'estudio'
        )

        for sol_estudio in estudios_solicitud:

            resultado = Resultado.objects.filter(
                solicitud_estudio=sol_estudio
            ).first()

            rangos = RangoReferencia.objects.filter(
                estudio=sol_estudio.estudio
            )

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

    return render(
        request,
        'analisis_bioquimico/portal/historial.html',
        context
    )
def detalle_pdf_resultados(request, solicitud_id):
    """
    Muestra una versión imprimible de los resultados
    de una solicitud finalizada del paciente autenticado.
    """

    paciente_id = request.session.get('paciente_id')

    if not paciente_id:
        messages.warning(
            request,
            'Debe ingresar con su DNI y CAP para consultar sus resultados.'
        )
        return redirect('analisis_bioquimico:login')

    paciente = get_object_or_404(
        Paciente,
        id=paciente_id
    )

    solicitud = get_object_or_404(
        SolicitudAnalisis.objects.select_related(
            'paciente',
            'estado',
            'receta__medico'
        ),
        id=solicitud_id,
        paciente=paciente
    )

    if solicitud.estado.nombre != 'Finalizada':
        messages.warning(
            request,
            'El informe todavía no está disponible porque la solicitud no está finalizada.'
        )

        return redirect(
            f"{request.build_absolute_uri('/portal/historial/')}?solicitud_id={solicitud.id}"
        )

    estudios_solicitud = SolicitudEstudio.objects.filter(
        solicitud=solicitud
    ).select_related(
        'estudio'
    ).order_by('id')

    resultados_detalle = []

    for solicitud_estudio in estudios_solicitud:

        resultado = Resultado.objects.filter(
            solicitud_estudio=solicitud_estudio
        ).select_related(
            'responsable'
        ).first()

        rangos = RangoReferencia.objects.filter(
            estudio=solicitud_estudio.estudio
        ).order_by(
            'edad_min'
        )

        resultados_detalle.append({
            'estudio': solicitud_estudio.estudio,
            'resultado': resultado,
            'rangos': rangos,
        })

    return render(
        request,
        'analisis_bioquimico/portal/detalle_pdf.html',
        {
            'paciente': paciente,
            'solicitud': solicitud,
            'resultados_detalle': resultados_detalle,
        }
    )

# ==========================================
# SECCIÓN: INSTITUCIONAL / HOME
# ==========================================

def home(request):
    return render(
        request,
        'analisis_bioquimico/home.html'
    )


# ==========================================
# SECCIÓN: LOGIN DE PERSONAL
# ==========================================

def login_personal(request):
    """
    Procesa el inicio de sesión del personal.

    La pantalla visual de acceso es portal/login.html.
    Esta vista recibe el formulario de la pestaña Personal
    y redirige según el rol del usuario.
    """

    # Si alguien entra manualmente a /personal/login/
    # lo enviamos al login unificado.
    if request.method != 'POST':
        return redirect(
            'analisis_bioquimico:login'
        )

    username = request.POST.get(
        'username',
        ''
    ).strip()

    password = request.POST.get(
        'password',
        ''
    )

    user = authenticate(
        request,
        username=username,
        password=password
    )

    if user is None:

        messages.error(
            request,
            'Usuario o contraseña incorrectos.'
        )

        return redirect(
            'analisis_bioquimico:login'
        )

    login(
        request,
        user
    )

    # --------------------------
    # Recepcionista
    # --------------------------

    if hasattr(user, 'recepcionista'):

        request.session['rol_personal'] = (
            'recepcionista'
        )

        return redirect(
            'analisis_bioquimico:panel_recepcion'
        )

    # --------------------------
    # Extraccionista
    # --------------------------

    if hasattr(user, 'extraccionista'):

        request.session['rol_personal'] = (
            'extraccionista'
        )

        return redirect(
            'analisis_bioquimico:panel_extraccion'
        )

    # --------------------------
    # Responsable de análisis
    # --------------------------

    if hasattr(user, 'responsable_analisis'):

        request.session['rol_personal'] = (
            'responsable'
        )

        return redirect(
            'analisis_bioquimico:panel_laboratorio'
        )

    # El usuario existe pero no está asociado
    # a ningún tipo de personal.

    logout(request)

    messages.error(
        request,
        'El usuario no tiene un rol de personal asignado.'
    )

    return redirect(
        'analisis_bioquimico:login'
    )


def logout_personal(request):
    """
    Cierra la sesión del personal.
    """

    logout(request)

    return redirect(
        'analisis_bioquimico:login'
    )


# ==========================================
# SECCIÓN: PANELES DEL PERSONAL
# ==========================================

def panel_recepcion(request):

    if not request.user.is_authenticated:

        return redirect(
            'analisis_bioquimico:login'
        )

    if not hasattr(
        request.user,
        'recepcionista'
    ):

        messages.error(
            request,
            'No tiene permisos para acceder a Recepción.'
        )

        return redirect(
            'analisis_bioquimico:login'
        )

    return render(
        request,
        'analisis_bioquimico/personal/panel_recepcion.html'
    )



def panel_extraccion(request):
    if not request.user.is_authenticated:
        return redirect('analisis_bioquimico:login')

    if not hasattr(request.user, 'extraccionista'):
        messages.error(
            request,
            'No tiene permisos para acceder a Extracción.'
        )
        return redirect('analisis_bioquimico:login')

    solicitudes_pendientes = (
        SolicitudAnalisis.objects.filter(
            estado__nombre__iexact='Pendiente de muestra'
        )
        .select_related('paciente', 'estado')
        .prefetch_related('solicitudestudio_set__estudio')
        .order_by('fecha_hora', 'id')
    )

    context = {
        'solicitudes': solicitudes_pendientes,
        'extraccionista': request.user.extraccionista,
    }

    return render(
        request,
        'analisis_bioquimico/personal/panel_extraccion.html',
        context
    )



def panel_laboratorio(request):

    if not request.user.is_authenticated:

        return redirect(
            'analisis_bioquimico:login'
        )

    if not hasattr(
        request.user,
        'responsable_analisis'
    ):

        messages.error(
            request,
            'No tiene permisos para acceder al Laboratorio.'
        )

        return redirect(
            'analisis_bioquimico:login'
        )

    return render(
        request,
        'analisis_bioquimico/personal/panel_laboratorio.html'
    )


# ==========================================
# SECCIÓN: MÓDULO 1 - RECEPCIÓN DE RECETA
# ==========================================

def recepcion_crear_solicitud(request):
    """
    Formulario para recepción de receta y creación
    de la solicitud inicial.
    """

    initial_data = {}

    if 'paciente_id' in request.GET:
        initial_data['paciente'] = request.GET.get(
            'paciente_id'
        )

    if 'medico_id' in request.GET:
        initial_data['medico'] = request.GET.get(
            'medico_id'
        )

    if request.method == 'POST':

        form = CrearSolicitudForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            paciente = form.cleaned_data[
                'paciente'
            ]

            medico = form.cleaned_data[
                'medico'
            ]

            fecha_emision = form.cleaned_data[
                'fecha_emision'
            ]

            archivo_pdf = form.cleaned_data[
                'archivo_pdf'
            ]

            estudios_seleccionados = (
                form.cleaned_data['estudios']
            )

            # --------------------------
            # 1. Crear receta
            # --------------------------

            receta = Receta.objects.create(
                paciente=paciente,
                medico=medico,
                fecha_emision=fecha_emision,
                archivo_pdf=archivo_pdf
            )

            # --------------------------
            # 2. Estado inicial
            # --------------------------

            estado_pendiente, _ = (
                EstadoSolicitud.objects.get_or_create(
                    nombre='Pendiente de muestra',
                    defaults={
                        'descripcion':
                        'Solicitud ingresada en recepción.'
                    }
                )
            )

            # --------------------------
            # 3. Recepcionista
            # --------------------------

            recepcionista = (
                Recepcionista.objects.first()
            )

            if not recepcionista:

                recepcionista = (
                    Recepcionista.objects.create(
                        nombre='Mesa de',
                        apellido='Entrada',
                        email=(
                            'recepcion@laboratoriosac.com.ar'
                        )
                    )
                )

            # --------------------------
            # 4. Solicitud
            # --------------------------

            solicitud = (
                SolicitudAnalisis.objects.create(
                    paciente=paciente,
                    receta=receta,
                    recepcionista=recepcionista,
                    estado=estado_pendiente
                )
            )

            # --------------------------
            # 5. Estudios
            # --------------------------

            for estudio in estudios_seleccionados:

                SolicitudEstudio.objects.create(
                    solicitud=solicitud,
                    estudio=estudio,
                    estado='Pendiente'
                )

            # --------------------------
            # 6. Email
            # --------------------------

            if paciente.email:

                asunto = (
                    'Laboratorio AC - '
                    f'Confirmación de Solicitud '
                    f'#{solicitud.id}'
                )

                estudios_texto = '\n'.join(
                    [
                        f'- {e.codigo}: {e.nombre}'
                        for e
                        in estudios_seleccionados
                    ]
                )

                mensaje = (
                    f'Hola {paciente.nombre} '
                    f'{paciente.apellido},\n\n'
                    f'Se ha registrado exitosamente '
                    f'tu solicitud #{solicitud.id}.\n\n'
                    f'Estudios:\n'
                    f'{estudios_texto}\n\n'
                    f'Aguarde en la sala de espera.\n\n'
                    f'Atentamente,\n'
                    f'Laboratorio AC'
                )

                try:

                    send_mail(
                        asunto,
                        mensaje,
                        'no-reply@laboratoriosac.com.ar',
                        [paciente.email],
                        fail_silently=True
                    )

                except Exception:
                    pass

            messages.success(
                request,
                f'Solicitud #{solicitud.id} '
                f'cargada exitosamente con su '
                f'receta escaneada para '
                f'{paciente.nombre} '
                f'{paciente.apellido}.'
            )

            return redirect(
                'analisis_bioquimico:recepcion_crear_solicitud'
            )

    else:

        form = CrearSolicitudForm(
            initial=initial_data
        )

    return render(
        request,
        'analisis_bioquimico/recepcion/crear_solicitud.html',
        {
            'form': form
        }
    )


# ==========================================
# SECCIÓN: MÓDULO 2 - GESTIÓN DE ESTUDIOS
# ==========================================

def estudios_lista(request):

    estudios = Estudio.objects.all().order_by(
        'codigo'
    )

    return render(
        request,
        'analisis_bioquimico/laboratorio/estudios/lista.html',
        {
            'estudios': estudios
        }
    )


def estudio_crear(request):

    if request.method == 'POST':

        form = EstudioForm(
            request.POST
        )

        if form.is_valid():

            estudio = form.save()

            messages.success(
                request,
                f'El estudio "{estudio.nombre}" '
                f'fue creado correctamente.'
            )

            return redirect(
                'analisis_bioquimico:estudios_lista'
            )

    else:

        form = EstudioForm()

    return render(
        request,
        'analisis_bioquimico/laboratorio/estudios/formulario.html',
        {
            'form': form,
            'titulo': 'Nuevo estudio',
        }
    )


def estudio_editar(
    request,
    estudio_id
):

    estudio = get_object_or_404(
        Estudio,
        id=estudio_id
    )

    if request.method == 'POST':

        form = EstudioForm(
            request.POST,
            instance=estudio
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f'El estudio "{estudio.nombre}" '
                f'fue actualizado correctamente.'
            )

            return redirect(
                'analisis_bioquimico:estudios_lista'
            )

    else:

        form = EstudioForm(
            instance=estudio
        )

    return render(
        request,
        'analisis_bioquimico/laboratorio/estudios/formulario.html',
        {
            'form': form,
            'titulo': 'Editar estudio',
            'estudio': estudio,
        }
    )


def estudio_eliminar(
    request,
    estudio_id
):

    estudio = get_object_or_404(
        Estudio,
        id=estudio_id
    )

    if request.method == 'POST':

        nombre = estudio.nombre

        estudio.delete()

        messages.success(
            request,
            f'El estudio "{nombre}" '
            f'fue eliminado correctamente.'
        )

        return redirect(
            'analisis_bioquimico:estudios_lista'
        )

    return render(
        request,
        'analisis_bioquimico/laboratorio/estudios/eliminar.html',
        {
            'estudio': estudio
        }
    )


def estudio_rangos(
    request,
    estudio_id
):

    estudio = get_object_or_404(
        Estudio,
        id=estudio_id
    )

    rangos = (
        RangoReferencia.objects.filter(
            estudio=estudio
        ).order_by(
            'edad_min'
        )
    )

    if request.method == 'POST':

        form = RangoReferenciaForm(
            request.POST
        )

        if form.is_valid():

            rango = form.save(
                commit=False
            )

            rango.estudio = estudio
            rango.save()

            messages.success(
                request,
                'El rango de referencia '
                'fue agregado correctamente.'
            )

            return redirect(
                'analisis_bioquimico:estudio_rangos',
                estudio_id=estudio.id
            )

    else:

        form = RangoReferenciaForm()

    return render(
        request,
        'analisis_bioquimico/laboratorio/estudios/rangos.html',
        {
            'estudio': estudio,
            'rangos': rangos,
            'form': form,
        }
    )


def rango_eliminar(
    request,
    rango_id
):

    rango = get_object_or_404(
        RangoReferencia,
        id=rango_id
    )

    estudio_id = rango.estudio.id

    if request.method == 'POST':

        rango.delete()

        messages.success(
            request,
            'El rango de referencia '
            'fue eliminado correctamente.'
        )

    return redirect(
        'analisis_bioquimico:estudio_rangos',
        estudio_id=estudio_id
    )


# ==========================================
# SECCIÓN: MÓDULO 2 - EXTRACCIÓN
# ==========================================

def sala_extraccion(request):
    """
    Lista solicitudes pendientes de extracción.
    """

    solicitudes_pendientes = (
        SolicitudAnalisis.objects.filter(
            estado__nombre__iexact='Pendiente'
        ).select_related(
            'paciente',
            'estado',
            'recepcionista'
        ).order_by(
            'fecha_hora'
        )
    )

    return render(
        request,
        'analisis_bioquimico/laboratorio/sala_extraccion.html',
        {
            'solicitudes': solicitudes_pendientes
        }
    )


def registrar_extraccion(request, solicitud_id):
    """
    Permite al extraccionista autenticado confirmar la toma de muestra.
    Registra la muestra, cambia la solicitud a Pendiente de análisis
    y genera el comprobante con su CAP.
    """

    if not request.user.is_authenticated:
        return redirect('analisis_bioquimico:login')

    if not hasattr(request.user, 'extraccionista'):
        messages.error(
            request,
            'No tiene permisos para registrar una extracción.'
        )
        return redirect('analisis_bioquimico:login')

    extraccionista = request.user.extraccionista

    solicitud = get_object_or_404(
        SolicitudAnalisis,
        id=solicitud_id,
        estado__nombre__iexact='Pendiente de muestra'
    )

    estudios = SolicitudEstudio.objects.filter(
        solicitud=solicitud
    ).select_related('estudio')

    if request.method == 'POST':

        tipo_muestra = request.POST.get(
            'tipo_muestra',
            ''
        ).strip()

        if not tipo_muestra:
            messages.error(
                request,
                'Debe indicar el tipo de muestra.'
            )

            return render(
                request,
                'analisis_bioquimico/personal/registrar_extraccion.html',
                {
                    'solicitud': solicitud,
                    'estudios': estudios,
                    'extraccionista': extraccionista,
                }
            )

        # ==========================================
        # 1. CREAR MUESTRA
        # ==========================================

        muestra = Muestra.objects.create(
            solicitud=solicitud,
            extraccionista=extraccionista,
            tipo=tipo_muestra
        )

        # ==========================================
        # 2. GENERAR COMPROBANTE + CAP
        # ==========================================

        comprobante = Comprobante.objects.create(
            solicitud=solicitud,
            muestra=muestra,
            numero_paciente=solicitud.paciente.id
        )

        # La CAP se genera automáticamente
        # en Comprobante.save()

        # ==========================================
        # 3. CAMBIAR ESTADO
        # ==========================================

        estado_pendiente_analisis, _ = (
            EstadoSolicitud.objects.get_or_create(
                nombre='Pendiente de análisis',
                defaults={
                    'descripcion':
                    'La toma de muestra fue completada y '
                    'la solicitud espera ser analizada.'
                }
            )
        )

        solicitud.estado = estado_pendiente_analisis
        solicitud.save()

        messages.success(
            request,
            f'Extracción registrada correctamente. '
            f'CAP generada: {comprobante.cap}'
        )

        # En vez de volver directamente al panel,
        # mostramos el comprobante.
        return redirect(
            'analisis_bioquimico:comprobante_extraccion',
            comprobante_id=comprobante.id
        )

    return render(
        request,
        'analisis_bioquimico/personal/registrar_extraccion.html',
        {
            'solicitud': solicitud,
            'estudios': estudios,
            'extraccionista': extraccionista,
        }
    )
def comprobante_extraccion(request, comprobante_id):
    """
    Muestra el comprobante generado después de la extracción.
    """

    if not request.user.is_authenticated:
        return redirect('analisis_bioquimico:login')

    if not hasattr(request.user, 'extraccionista'):
        messages.error(
            request,
            'No tiene permisos para ver este comprobante.'
        )
        return redirect('analisis_bioquimico:login')

    comprobante = get_object_or_404(
        Comprobante.objects.select_related(
            'solicitud__paciente',
            'solicitud__receta__medico',
            'muestra__extraccionista'
        ),
        id=comprobante_id
    )

    estudios = SolicitudEstudio.objects.filter(
        solicitud=comprobante.solicitud
    ).select_related('estudio')

    return render(
        request,
        'analisis_bioquimico/personal/comprobante_extraccion.html',
        {
            'comprobante': comprobante,
            'solicitud': comprobante.solicitud,
            'muestra': comprobante.muestra,
            'estudios': estudios,
        }
    )

def panel_bioquimico(request):
    """
    Muestra las solicitudes pendientes de análisis
    y aquellas que ya están en análisis.
    """

    if not request.user.is_authenticated:
        return redirect('analisis_bioquimico:login')

    if not hasattr(request.user, 'responsable_analisis'):
        messages.error(
            request,
            'No tiene permisos para acceder al panel del bioquímico.'
        )
        return redirect('analisis_bioquimico:login')

    solicitudes = SolicitudAnalisis.objects.filter(
        estado__nombre__in=[
            'Pendiente de análisis',
            'En análisis'
        ]
    ).select_related(
        'paciente',
        'estado'
    ).order_by('fecha_hora', 'id')

    return render(
        request,
        'analisis_bioquimico/personal/panel_bioquimico.html',
        {'solicitudes': solicitudes}
    )


@require_http_methods(["GET", "POST"])
def cargar_resultados(request, solicitud_id):
    """
    Permite registrar los resultados de los estudios
    de una solicitud y actualizar su estado.
    """

    if not request.user.is_authenticated:
        return redirect('analisis_bioquimico:login')

    if not hasattr(request.user, 'responsable_analisis'):
        messages.error(
            request,
            'No tiene permisos para cargar resultados.'
        )
        return redirect('analisis_bioquimico:login')

    solicitud = get_object_or_404(
        SolicitudAnalisis.objects.select_related(
            'paciente',
            'estado'
        ),
        pk=solicitud_id,
        estado__nombre__in=[
            'Pendiente de análisis',
            'En análisis'
        ]
    )

    detalles = SolicitudEstudio.objects.filter(
        solicitud=solicitud
    ).select_related('estudio').order_by('id')

    resultados_existentes = {
        resultado.solicitud_estudio_id: resultado
        for resultado in Resultado.objects.filter(
            solicitud_estudio__solicitud=solicitud
        ).order_by('id')
    }

    if request.method == 'POST':
        valores_nuevos = {}

        # Validar todos los valores antes de guardar.
        for detalle in detalles:
            campo = f'valor_{detalle.id}'
            texto = request.POST.get(campo, '').strip()

            if not texto:
                continue

            try:
                valor = Decimal(texto.replace(',', '.'))

                if not valor.is_finite():
                    raise InvalidOperation

                valores_nuevos[detalle.id] = float(valor)

            except (InvalidOperation, ValueError, OverflowError):
                messages.error(
                    request,
                    f'Valor inválido para {detalle.estudio.nombre}.'
                )
                return redirect(
                    'analisis_bioquimico:cargar_resultados',
                    solicitud_id=solicitud.id
                )

        with transaction.atomic():

            solicitud = SolicitudAnalisis.objects.select_for_update().get(
                pk=solicitud.id
            )

            if solicitud.estado.nombre not in [
                'Pendiente de análisis',
                'En análisis'
            ]:
                messages.warning(
                    request,
                    'La solicitud ya no admite nuevos resultados.'
                )
                return redirect(
                    'analisis_bioquimico:panel_bioquimico'
                )

            responsable = request.user.responsable_analisis

            for detalle in detalles:
                if detalle.id not in valores_nuevos:
                    continue

                Resultado.objects.update_or_create(
                    solicitud_estudio=detalle,
                    defaults={
                        'responsable': responsable,
                        'valor_hallado': valores_nuevos[detalle.id]
                    }
                )

            total_estudios = detalles.count()

            total_completados = Resultado.objects.filter(
                solicitud_estudio__solicitud=solicitud
            ).values(
                'solicitud_estudio_id'
            ).distinct().count()

            if total_estudios > 0 and total_completados == total_estudios:
                nombre_estado = 'Finalizada'

            elif total_completados > 0:
                nombre_estado = 'En análisis'

            else:
                nombre_estado = 'Pendiente de análisis'

            estado, _ = EstadoSolicitud.objects.get_or_create(
                nombre=nombre_estado
            )

            estado_anterior = solicitud.estado.nombre

            solicitud.estado = estado
            solicitud.save(update_fields=['estado'])

            if (
                estado_anterior != 'Finalizada'
                and nombre_estado == 'Finalizada'
            ):
                transaction.on_commit(
                    lambda solicitud_id=solicitud.id:
                        enviar_email_finalizacion(solicitud_id)
                )

        if nombre_estado == 'Finalizada':
            messages.success(
                request,
                f'La solicitud #{solicitud.id} fue finalizada correctamente.'
            )
            return redirect(
                'analisis_bioquimico:panel_bioquimico'
            )

        messages.success(
            request,
            f'Resultados guardados. Estado: {nombre_estado}.'
        )

        return redirect(
            'analisis_bioquimico:cargar_resultados',
            solicitud_id=solicitud.id
        )

    # Preparar los datos para el template.
    detalles_resultados = []

    for detalle in detalles:
        detalles_resultados.append({
            'id': detalle.id,
            'estudio': detalle.estudio,
            'resultado': resultados_existentes.get(detalle.id),
            'rangos': RangoReferencia.objects.filter(
                estudio=detalle.estudio
            ).order_by('edad_min')
        })

    return render(
        request,
        'analisis_bioquimico/personal/cargar_resultados.html',
        {
            'solicitud': solicitud,
            'detalles': detalles_resultados
        }
    )