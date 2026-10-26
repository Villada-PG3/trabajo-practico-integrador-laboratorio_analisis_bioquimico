from django.test import TestCase

# Create your tests here.
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings

from .models import (
    EstadoSolicitud,
    Notificacion,
    Paciente,
    Recepcionista,
    SolicitudAnalisis,
)
from .services import enviar_email_finalizacion


@override_settings(
    MAILERS={
        "default": {
            "BACKEND": "django.core.mail.backends.locmem.EmailBackend",
        }
    }
)
class EmailFinalizacionTests(TestCase):

    def setUp(self):
        self.paciente = Paciente.objects.create(
            nombre="Carlos",
            apellido="Gomez",
            dni="12345678",
            email="carlos@example.com",
        )

        self.recepcionista = Recepcionista.objects.create(
            nombre="Ana",
            apellido="Lopez",
        )

        self.estado_finalizada = EstadoSolicitud.objects.create(
            nombre="Finalizada"
        )

        self.estado_pendiente = EstadoSolicitud.objects.create(
            nombre="Pendiente de análisis"
        )

        self.solicitud = SolicitudAnalisis.objects.create(
            paciente=self.paciente,
            recepcionista=self.recepcionista,
            estado=self.estado_finalizada,
        )

    def test_envio_exitoso(self):
        resultado = enviar_email_finalizacion(self.solicitud.id)

        self.assertTrue(resultado)
        self.assertEqual(len(mail.outbox), 1)

        correo = mail.outbox[0]

        self.assertEqual(correo.to, ["carlos@example.com"])
        self.assertIn("Resultados disponibles", correo.subject)
        self.assertIn(str(self.solicitud.id), correo.body)
        self.assertTrue(
            any(tipo == "text/html" for _, tipo in correo.alternatives)
        )

        self.assertTrue(
            Notificacion.objects.filter(
                solicitud=self.solicitud,
                tipo="Finalizacion",
                estado="Enviada",
            ).exists()
        )

    def test_no_envia_duplicados(self):
        primer_envio = enviar_email_finalizacion(self.solicitud.id)
        segundo_envio = enviar_email_finalizacion(self.solicitud.id)

        self.assertTrue(primer_envio)
        self.assertFalse(segundo_envio)
        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(
            Notificacion.objects.filter(
                solicitud=self.solicitud,
                tipo="Finalizacion",
                estado="Enviada",
            ).count(),
            1,
        )

    def test_no_envia_si_solicitud_no_finalizada(self):
        self.solicitud.estado = self.estado_pendiente
        self.solicitud.save(update_fields=["estado"])

        resultado = enviar_email_finalizacion(self.solicitud.id)

        self.assertFalse(resultado)
        self.assertEqual(len(mail.outbox), 0)
        self.assertEqual(Notificacion.objects.count(), 0)

    def test_paciente_sin_email(self):
        self.paciente.email = None
        self.paciente.save(update_fields=["email"])

        resultado = enviar_email_finalizacion(self.solicitud.id)

        self.assertFalse(resultado)
        self.assertEqual(len(mail.outbox), 0)

        self.assertTrue(
            Notificacion.objects.filter(
                solicitud=self.solicitud,
                tipo="Finalizacion",
                estado="Sin email",
            ).exists()
        )

    @patch("analisis_bioquimico.services.EmailMultiAlternatives.send")
    def test_error_de_envio(self, mock_send):
        mock_send.side_effect = ConnectionError(
            "Error simulado del servidor de correo"
        )

        resultado = enviar_email_finalizacion(self.solicitud.id)

        self.assertFalse(resultado)

        self.assertTrue(
            Notificacion.objects.filter(
                solicitud=self.solicitud,
                tipo="Finalizacion",
                estado="Error",
            ).exists()
        )

        self.solicitud.refresh_from_db()
        self.assertEqual(self.solicitud.estado.nombre, "Finalizada")