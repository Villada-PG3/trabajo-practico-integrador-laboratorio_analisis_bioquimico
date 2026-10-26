import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from .models import Notificacion


logger = logging.getLogger(__name__)


def enviar_email_finalizacion(solicitud_id):
    """
    Envía un correo HTML cuando una solicitud finaliza
    y registra el resultado del intento de envío.
    """

    from .models import SolicitudAnalisis

    solicitud = SolicitudAnalisis.objects.select_related(
        'paciente', 'estado'
    ).get(pk=solicitud_id)

    if solicitud.estado.nombre != 'Finalizada':
        return False

    # Evitar reenviar si ya existe un envío exitoso.
    if Notificacion.objects.filter(
        solicitud=solicitud,
        tipo='Finalizacion',
        estado='Enviada'
    ).exists():
        return False

    paciente = solicitud.paciente

    if not paciente.email:
        Notificacion.objects.create(
            solicitud=solicitud,
            tipo='Finalizacion',
            estado='Sin email'
        )
        return False

    asunto = (
        f'Laboratorio AC - Resultados disponibles '
        f'- Solicitud #{solicitud.id}'
    )

    contexto = {
        'paciente': paciente,
        'solicitud': solicitud,
    }

    html = render_to_string(
        'analisis_bioquimico/emails/finalizacion.html',
        contexto
    )

    texto = (
        f'Hola {paciente.nombre} {paciente.apellido}.\n\n'
        f'Los resultados de tu solicitud #{solicitud.id} '
        'ya están disponibles.\n\n'
        'Podés consultarlos ingresando al portal de pacientes '
        'con tu DNI y tu Clave de Acceso Personal (CAP).\n\n'
        'Laboratorio AC'
    )

    mensaje = EmailMultiAlternatives(
        subject=asunto,
        body=texto,
        from_email=getattr(
            settings,
            'DEFAULT_FROM_EMAIL',
            'no-reply@laboratoriosac.com.ar'
        ),
        to=[paciente.email]
    )

    mensaje.attach_alternative(html, 'text/html')

    try:
        cantidad_enviada = mensaje.send(fail_silently=False)

    except Exception:
        logger.exception(
            'Error enviando email de solicitud %s',
            solicitud.id
        )

        Notificacion.objects.create(
            solicitud=solicitud,
            tipo='Finalizacion',
            estado='Error'
        )
        return False

    if cantidad_enviada == 1:
        Notificacion.objects.create(
            solicitud=solicitud,
            tipo='Finalizacion',
            estado='Enviada'
        )
        return True

    Notificacion.objects.create(
        solicitud=solicitud,
        tipo='Finalizacion',
        estado='Error'
    )
    return False