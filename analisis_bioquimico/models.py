from django.db import models


class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    dni = models.CharField(max_length=15, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    domicilio = models.CharField(max_length=200, blank=True, null=True)
    cap = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.apellido}, {self.nombre} (DNI: {self.dni})"


class Medico(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    matricula = models.CharField(max_length=50, unique=True)
    especialidad = models.CharField(max_length=100)
    validado_colegio = models.BooleanField(default=False)

    def __str__(self):
        return f"Dr. {self.apellido}, {self.nombre}"


class Recepcionista(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Recepcionista: {self.apellido}, {self.nombre}"


class Extraccionista(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    legajo = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"Extraccionista: {self.apellido}, {self.nombre}"


class ResponsableAnalisis(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    legajo = models.CharField(max_length=50, unique=True)
    cargo = models.CharField(max_length=100)

    def __str__(self):
        return f"Bioquímico: {self.apellido}, {self.nombre}"


class EstadoSolicitud(models.Model):
    nombre = models.CharField(max_length=50)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class Estudio(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    metodo_tecnica = models.CharField(max_length=100, blank=True, null=True)
    unidad_medida = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class RangoReferencia(models.Model):
    estudio = models.ForeignKey(Estudio, on_delete=models.CASCADE)
    valor_min = models.FloatField()
    valor_max = models.FloatField()
    genero = models.CharField(max_length=20, blank=True, null=True)
    edad_min = models.IntegerField(default=0)
    edad_max = models.IntegerField(default=120)

    def __str__(self):
        return f"Rango {self.estudio.nombre} ({self.valor_min} - {self.valor_max})"


class Receta(models.Model):
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    fecha_emision = models.DateField()
    archivo_pdf = models.FileField(upload_to='recetas/', blank=True, null=True)

    def __str__(self):
        return f"Receta #{self.id} - Paciente: {self.paciente.apellido}"



class SolicitudAnalisis(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    receta = models.ForeignKey(Receta, on_delete=models.SET_NULL, null=True, blank=True)
    recepcionista = models.ForeignKey(Recepcionista, on_delete=models.CASCADE)
    estado = models.ForeignKey(EstadoSolicitud, on_delete=models.PROTECT)
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Solicitud #{self.id} - {self.paciente.apellido}"


class SolicitudEstudio(models.Model):
    solicitud = models.ForeignKey(SolicitudAnalisis, on_delete=models.CASCADE)
    estudio = models.ForeignKey(Estudio, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50, default='Pendiente')

    def __str__(self):
        return f"Solicitud #{self.solicitud.id} / Estudio: {self.estudio.nombre}"


class Muestra(models.Model):
    solicitud = models.ForeignKey(SolicitudAnalisis, on_delete=models.CASCADE)
    extraccionista = models.ForeignKey(Extraccionista, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    fecha_hora_extraccion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Muestra #{self.id} ({self.tipo}) - Solicitud #{self.solicitud.id}"


class Resultado(models.Model):
    solicitud_estudio = models.ForeignKey(SolicitudEstudio, on_delete=models.CASCADE)
    responsable = models.ForeignKey(ResponsableAnalisis, on_delete=models.CASCADE)
    valor_hallado = models.FloatField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resultado: {self.valor_hallado} ({self.solicitud_estudio.estudio.nombre})"


class Comprobante(models.Model):
    solicitud = models.ForeignKey(SolicitudAnalisis, on_delete=models.CASCADE)
    muestra = models.ForeignKey(Muestra, on_delete=models.CASCADE)
    fecha_emision = models.DateTimeField(auto_now_add=True)
    cap = models.CharField(max_length=50, blank=True, null=True)
    numero_paciente = models.IntegerField()

    def __str__(self):
        return f"Comprobante #{self.id} - Solicitud #{self.solicitud.id}"


class Notificacion(models.Model):
    solicitud = models.ForeignKey(SolicitudAnalisis, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50)
    estado = models.CharField(max_length=50)
    fecha_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notificación {self.tipo} - Solicitud #{self.solicitud.id}"