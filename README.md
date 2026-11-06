# SAC - Sistema de Análisis Bioquímicos

## Descripción del proyecto

SAC es una aplicación web desarrollada con Python y Django para gestionar el funcionamiento de un laboratorio de análisis bioquímicos.

El sistema permite administrar pacientes, médicos, recetas, solicitudes de análisis, estudios, muestras y resultados, acompañando el proceso desde la recepción del paciente hasta la consulta de sus resultados.

Este proyecto fue desarrollado como Trabajo Práctico Integrador de sexto año de secundaria, tomando como referencia el dominio de un laboratorio de análisis bioquímicos de Córdoba, Argentina.

## Objetivos

- Centralizar la información del laboratorio en una base de datos.
- Registrar pacientes y médicos.
- Validar las matrículas profesionales de los médicos mediante un servicio simulado.
- Gestionar recetas y solicitudes de análisis.
- Registrar extracciones de muestras.
- Cargar los resultados de los estudios solicitados.
- Permitir que los pacientes consulten sus resultados.
- Generar comprobantes con una Clave de Acceso Personal (CAP).
- Enviar notificaciones relacionadas con las solicitudes.
- Consultar reportes estadísticos del laboratorio.

## Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python | Lenguaje de programación principal |
| Django 6.1.1 | Framework web |
| SQLite | Base de datos durante el desarrollo |
| HTML | Estructura de las páginas |
| CSS y Bootstrap 5 | Diseño de las interfaces |
| JavaScript | Interactividad y actualización de la sala de espera |
| Chart.js | Visualización de reportes estadísticos |
| Pillow | Soporte para procesamiento de imágenes |
| Git y GitHub | Control de versiones y trabajo colaborativo |

Las dependencias Python están especificadas en `requirements.txt`.

## Arquitectura del proyecto

El proyecto utiliza la arquitectura de Django y está organizado alrededor de una única aplicación llamada `analisis_bioquimico`.

Esta aplicación contiene los modelos, formularios, vistas, rutas y templates necesarios para los distintos módulos del laboratorio.

Los datos se almacenan en la base de datos mediante el ORM de Django, evitando definir pacientes, médicos o empleados directamente en el código.

## Actores del sistema

### Paciente

Puede ingresar al portal utilizando su DNI y la Clave de Acceso Personal (CAP), consultar su historial de solicitudes y acceder a los informes de las solicitudes finalizadas.

### Médico

Es el profesional que emite la receta médica e indica los estudios que debe realizarse el paciente.

Su matrícula profesional debe estar habilitada para que pueda ser seleccionado al registrar una solicitud.

### Recepcionista

Se encarga de buscar y registrar pacientes, actualizar sus datos de contacto, validar médicos, recibir recetas y crear solicitudes.

### Extraccionista

Consulta las solicitudes pendientes, llama a los pacientes, registra la toma de muestras y genera los comprobantes con CAP.

### Responsable de Análisis

Administra el catálogo de estudios y sus rangos de referencia, carga los resultados y consulta los reportes estadísticos.

## Funcionalidades implementadas

### 1. Gestión de pacientes

El recepcionista puede buscar pacientes mediante su DNI.

Si el paciente existe, puede modificar sus datos de contacto. Si no existe, puede registrarlo en la base de datos.

El DNI es único para evitar duplicaciones.

### 2. Gestión de médicos

Se implementó una simulación del servicio de validación de matrículas profesionales del Colegio Médico.

El recepcionista ingresa una matrícula y el sistema consulta un registro simulado almacenado en la base de datos.

La consulta devuelve una respuesta JSON con el estado de habilitación y los datos del médico.

Si la matrícula está habilitada, el médico puede registrarse o actualizarse en la base de datos del laboratorio.

**Aclaración:** esta funcionalidad simula el servicio externo. No realiza consultas al Colegio Médico real.

### 3. Recepción de recetas y solicitudes

El recepcionista registra una nueva solicitud vinculando:

- Paciente.
- Médico solicitante.
- Fecha de emisión de la receta.
- Archivo escaneado de la receta.
- Estudios solicitados.

La fecha de la receta no puede ser futura ni superar los 30 días de antigüedad.

Al registrar una solicitud, su estado inicial es `Pendiente de muestra`.

También se genera una notificación por correo electrónico para confirmar el registro.

### 4. Sala de espera

El extraccionista puede llamar a los pacientes pendientes.

La pantalla pública de sala de espera muestra el nombre del paciente y el número de solicitud.

La información se actualiza automáticamente mediante JavaScript y consultas periódicas a Django.

Una vez completada la extracción, la solicitud deja de aparecer como pendiente en la sala de espera.

### 5. Extracción y comprobante

El extraccionista selecciona una solicitud y registra el tipo de muestra obtenida.

Después de confirmar la extracción:

- Se guarda la muestra.
- Se identifica al extraccionista responsable.
- Se genera un comprobante.
- Se genera una CAP para que el paciente pueda consultar sus resultados.
- La solicitud pasa al estado `Pendiente de análisis`.

### 6. Gestión de estudios

El Responsable de Análisis puede crear, consultar, editar y eliminar estudios, además de administrar sus rangos de referencia.

Cada estudio puede tener un código, nombre, descripción, método o técnica, unidad de medida y rangos de referencia.

### 7. Carga de resultados

El Responsable de Análisis registra los valores hallados de cada estudio solicitado.

Cuando se carga el primer resultado, la solicitud pasa a `En análisis`.

Cuando todos los estudios tienen resultados registrados, la solicitud pasa automáticamente a `Finalizada`.

Al finalizar se genera una notificación para el paciente.

### 8. Portal del paciente

El paciente inicia sesión mediante DNI y CAP.

Desde el portal puede consultar su historial de solicitudes y conocer el estado de cada una.

Los resultados solamente están disponibles cuando la solicitud se encuentra finalizada.

También puede abrir una versión imprimible del informe y utilizar la opción del navegador para guardarlo como PDF.

**Aclaración:** el informe se imprime o guarda como PDF mediante el navegador, no mediante un generador de PDF del servidor.

### 9. Reportes estadísticos

El Responsable de Análisis puede consultar gráficos estadísticos que muestran el volumen de solicitudes.

Los reportes permiten agrupar los registros por día, semana o mes y filtrar por estudio.

### 10. Autenticación y permisos

El sistema utiliza la autenticación de Django para los empleados.

Los pacientes utilizan un acceso independiente mediante DNI y CAP.

Las vistas protegidas verifican el rol correspondiente antes de permitir el acceso a las funciones.

El sistema impide que un paciente consulte informes pertenecientes a otro paciente.

## Estados de una solicitud

Una solicitud atraviesa las siguientes etapas:

```text
Pendiente de muestra
        |
        v
Pendiente de análisis
        |
        v
En análisis
        |
        v
Finalizada
```

Los cambios de estado se realizan de acuerdo con las operaciones registradas en el sistema.

## Estructura general del proyecto

```text
proyecto/
|
|-- analisis_bioquimico/
|   |-- migrations/
|   |-- templates/
|   |   `-- analisis_bioquimico/
|   |       |-- personal/
|   |       |-- portal/
|   |       |-- recepcion/
|   |       |-- laboratorio/
|   |       `-- sala_espera.html
|   |
|   |-- admin.py
|   |-- apps.py
|   |-- forms.py
|   |-- models.py
|   |-- permisos.py
|   |-- services.py
|   |-- urls.py
|   `-- views.py
|
|-- config/
|   |-- settings.py
|   |-- urls.py
|   |-- asgi.py
|   `-- wsgi.py
|
|-- docs/
|-- manage.py
|-- requirements.txt
|-- README.md
`-- .gitignore
```

La carpeta `docs/` está destinada a contener el Diagrama Entidad-Relación (DER) y el Diagrama de Clases UML.

## Instalación del proyecto

### Requisitos previos

- Python compatible con las dependencias del proyecto.
- Git.
- Una terminal.
- Acceso al repositorio.

### 1. Clonar el repositorio

```bash
git clone https://github.com/Villada-PG3/trabajo-practico-integrador-laboratorio_analisis_bioquimico.git

cd trabajo-practico-integrador-laboratorio_analisis_bioquimico
```

### 2. Crear el entorno virtual

```bash
python -m venv .venv
```

### 3. Activar el entorno virtual

En Linux o macOS:

```bash
source .venv/bin/activate
```

En Windows (CMD):

```bat
.venv\Scripts\activate
```

En Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Instalar las dependencias

```bash
python -m pip install -r requirements.txt
```

### 5. Aplicar las migraciones

```bash
python manage.py migrate
```

Las migraciones existentes crean las tablas necesarias para almacenar los datos del laboratorio.

### 6. Crear un superusuario

```bash
python manage.py createsuperuser
```

El superusuario permite acceder al administrador de Django y gestionar los registros iniciales.

### 7. Iniciar el servidor

```bash
python manage.py runserver
```

El sistema estará disponible normalmente en:

`http://127.0.0.1:8000/`

El administrador de Django estará disponible en:

`http://127.0.0.1:8000/admin/`

## Configuración inicial

Después de aplicar las migraciones, deben cargarse los datos necesarios para utilizar el sistema, incluyendo:

- Usuarios del personal.
- Recepcionistas.
- Extraccionistas.
- Responsables de análisis.
- Estudios y rangos de referencia.
- Matrículas del Colegio Médico simulado, para probar la validación.

Los usuarios del personal deben estar asociados a su correspondiente registro de empleado.

Los datos se cargan en la base de datos y no se encuentran definidos directamente en el código.

## Correos electrónicos

Durante el desarrollo, el proyecto utiliza el backend de correo por consola de Django.

Esto permite comprobar los mensajes generados por el sistema sin realizar envíos reales a direcciones externas.

Para utilizar correos reales será necesario configurar un proveedor de email y sus credenciales.

## Modelos de datos

Los modelos principales del laboratorio son:

- `Paciente`
- `Medico`
- `Recepcionista`
- `Extraccionista`
- `ResponsableAnalisis`
- `EstadoSolicitud`
- `Estudio`
- `RangoReferencia`
- `Receta`
- `SolicitudAnalisis`
- `SolicitudEstudio`
- `Muestra`
- `Resultado`
- `Comprobante`
- `Notificacion`
- `MatriculaColegioSimulado`
- `LlamadoExtraccion`

Las relaciones entre modelos se implementan mediante campos como `ForeignKey` y `OneToOneField` de Django.

## Diagramas

El diseño del proyecto se documenta mediante:

- Diagrama Entidad-Relación (DER).
- Diagrama de Clases UML.

Estos diagramas deben mantenerse en la carpeta `docs/` del repositorio.

## Metodología de trabajo con GitHub

El proyecto se desarrolló de manera colaborativa utilizando Git y GitHub.

Se utiliza una rama `main` como base principal del proyecto.

Cada funcionalidad o corrección se desarrolla en una rama independiente con un nombre descriptivo, por ejemplo:

```text
feature/recepcion-completa
feature/sala-espera
feature/permisos-seguridad
```

Una vez probados los cambios, se realiza un commit y se sube la rama a GitHub.

Después se crea un Pull Request para revisar e incorporar los cambios a `main`.

Esta metodología permite mantener un historial de cambios y facilitar la recuperación de versiones anteriores.

## Pruebas realizadas

Se realizó una prueba integral del sistema recorriendo las siguientes etapas:

1. Registro de paciente.
2. Validación del médico.
3. Carga de receta y creación de solicitud.
4. Llamado en sala de espera.
5. Registro de extracción.
6. Generación del comprobante y CAP.
7. Carga parcial y completa de resultados.
8. Finalización automática de la solicitud.
9. Consulta de resultados mediante DNI y CAP.
10. Impresión y guardado del informe como PDF.

También se probaron los controles de acceso por roles y la restricción para consultar informes de otros pacientes.

Estas comprobaciones corresponden a pruebas funcionales manuales.

## Alcance y limitaciones

El sistema fue desarrollado con fines académicos.

La validación del Colegio Médico es simulada, los correos electrónicos se muestran en consola durante el desarrollo y los PDF de resultados se obtienen mediante la función de impresión del navegador.

La aplicación no está preparada para utilizarse con información médica real en un entorno de producción sin realizar verificaciones adicionales de seguridad, privacidad, configuración y funcionamiento.

## Estado del proyecto

Los módulos funcionales principales se encuentran implementados y fueron probados mediante un recorrido integral del sistema.

El proyecto se encuentra en la etapa de documentación y preparación para la presentación final.