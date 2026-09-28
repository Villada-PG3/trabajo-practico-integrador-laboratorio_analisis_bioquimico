# SAC - Sistema de Análisis Bioquímicos

## Descripción

SAC (Sistema de Análisis Bioquímicos) es una aplicación web desarrollada
con Django para la gestión de las solicitudes de análisis de un laboratorio
de análisis bioquímicos.

El sistema busca centralizar la información de los pacientes, médicos,
recetas, solicitudes de análisis, estudios, muestras y resultados,
permitiendo gestionar las distintas etapas del proceso dentro del laboratorio.

El proyecto se desarrolla como parte de un Trabajo Práctico Integrador y
está basado en el dominio de un laboratorio de análisis bioquímicos
de la ciudad de Córdoba, Argentina.

Actualmente, el proyecto se encuentra en una etapa inicial de desarrollo.
Se han definido los principales modelos de datos y la estructura general
de la aplicación. Las funcionalidades y las interfaces del sistema se
incorporarán progresivamente.

## Objetivos del sistema

- Gestionar la información de los pacientes y los profesionales del laboratorio.
- Registrar recetas médicas y solicitudes de análisis.
- Administrar los estudios que realiza el laboratorio.
- Gestionar la extracción de muestras.
- Registrar los resultados obtenidos para cada estudio.
- Permitir la consulta de las solicitudes y los resultados por parte de los pacientes.
- Facilitar el seguimiento del estado de las solicitudes.
- Generar comprobantes y notificaciones asociados al proceso.
- Proporcionar información estadística sobre las solicitudes de análisis.

## Dominio y funcionamiento

El sistema contempla el proceso de atención de un paciente en un laboratorio
de análisis bioquímicos.

El flujo de trabajo previsto es el siguiente:

1. **Registro de la solicitud:** el recepcionista recibe la receta médica,
   verifica los datos del paciente y registra la solicitud con los estudios
   correspondientes.

2. **Validación de la receta:** se contempla la validación de la matrícula
   profesional del médico y el control de la fecha de emisión de la receta.

3. **Recepción y espera:** una vez registrada la solicitud, el paciente
   queda a la espera de la extracción de las muestras.

4. **Extracción de muestras:** un extraccionista se encarga de obtener las
   muestras necesarias y registrar la extracción en el sistema.

5. **Realización de los estudios:** el responsable de análisis registra
   los valores obtenidos para los estudios solicitados.

6. **Finalización:** cuando se completan los estudios de una solicitud,
   esta pasa al estado de finalizada.

7. **Consulta de resultados:** se prevé que el paciente pueda consultar
   sus solicitudes y los resultados disponibles mediante sus datos de acceso.

8. **Notificaciones y comprobantes:** el sistema contempla la generación
   de comprobantes y el envío de notificaciones relacionadas con las
   solicitudes y la disponibilidad de resultados.

Este flujo describe el funcionamiento previsto del sistema. Las etapas se
irán implementando a medida que avance el desarrollo.

## Actores del sistema

El dominio contempla los siguientes actores:

- **Paciente:** solicita análisis y consulta sus solicitudes y resultados.
- **Médico:** emite las recetas que indican los estudios que debe realizarse
  el paciente.
- **Recepcionista:** registra las solicitudes y gestiona los datos necesarios
  para iniciar el proceso.
- **Extraccionista:** realiza y registra la extracción de las muestras.
- **Responsable de análisis:** registra los resultados de los estudios.
- **Responsable de laboratorio:** consulta información estadística sobre
  las solicitudes y los estudios realizados.

Los permisos, las interfaces y las operaciones específicas de cada actor
se incorporarán durante el desarrollo.

## Funcionalidades previstas

Las funcionalidades contempladas para el sistema son:

### Gestión de pacientes y profesionales
- Registro y consulta de pacientes.
- Actualización de los datos de contacto de los pacientes.
- Registro de médicos y sus matrículas profesionales.
- Gestión de recepcionistas, extraccionistas y responsables de análisis.

### Gestión de recetas y solicitudes
- Registro de recetas médicas.
- Almacenamiento de recetas en formato PDF.
- Creación de solicitudes de análisis.
- Asociación de pacientes, recetas y recepcionistas.
- Selección de los estudios correspondientes a cada solicitud.
- Seguimiento del estado de las solicitudes.

### Gestión de estudios y muestras
- Administración del catálogo de estudios.
- Definición de rangos de referencia para los estudios.
- Registro de muestras y de los responsables de su extracción.
- Seguimiento de las etapas de procesamiento de las muestras.

### Gestión de resultados
- Registro de resultados asociados a los estudios solicitados.
- Asociación de los resultados con el responsable de análisis.
- Consulta de los valores obtenidos y sus rangos de referencia.

### Comprobantes y notificaciones
- Generación de comprobantes asociados a las solicitudes.
- Registro de notificaciones relacionadas con el proceso.
- Notificación al paciente sobre la disponibilidad de sus resultados.

### Reportes
- Consulta de la cantidad de solicitudes por período.
- Posibilidad de discriminar la información por estudio.
- Generación de reportes estadísticos para el laboratorio.

Las funcionalidades enumeradas representan los objetivos del proyecto y no
implican que todas estén disponibles en la versión actual.

## Tecnologías utilizadas

Las tecnologías y herramientas utilizadas actualmente son:

- **Python:** lenguaje de programación.
- **Django 6.1.1:** framework para el desarrollo web.
- **SQLite:** motor de base de datos utilizado durante el desarrollo.
- **Pillow 12.3.0:** biblioteca de procesamiento de imágenes incluida
  entre las dependencias del proyecto.

Las dependencias se encuentran especificadas en el archivo
`requirements.txt`.

## Modelo de datos

El sistema utiliza modelos de Django para representar las entidades
principales del dominio.

Los modelos se encuentran definidos en:

`analisis_bioquimico/models.py`

### Entidades principales

| Entidad | Descripción |
|---|---|
| Paciente | Almacena los datos personales y de contacto del paciente. |
| Medico | Representa al profesional que emite las recetas. |
| Recepcionista | Representa al personal que registra las solicitudes. |
| Extraccionista | Representa al personal encargado de extraer las muestras. |
| ResponsableAnalisis | Representa al responsable de registrar los resultados. |
| EstadoSolicitud | Define los estados disponibles para las solicitudes. |
| Estudio | Contiene la información de los análisis que realiza el laboratorio. |
| RangoReferencia | Define los rangos de referencia asociados a los estudios. |
| Receta | Almacena la información de la receta médica y el archivo PDF. |
| SolicitudAnalisis | Representa una solicitud de análisis de un paciente. |
| SolicitudEstudio | Relaciona una solicitud con cada estudio requerido. |
| Muestra | Registra las muestras asociadas a una solicitud. |
| Resultado | Almacena el valor obtenido para un estudio solicitado. |
| Comprobante | Registra los comprobantes asociados a las solicitudes y muestras. |
| Notificacion | Registra las notificaciones relacionadas con una solicitud. |

Las relaciones entre las entidades se implementan mediante campos de tipo
`ForeignKey` y las reglas de integridad correspondientes de Django.

### Diagramas

La documentación del modelo y del diseño se encuentra en la carpeta `docs/`.

- **Diagrama Entidad-Relación:** `docs/diagramaER.mmd`
- **Diagrama UML:** `docs/diagramaUML.mmd`

Los diagramas representan el diseño del sistema y se actualizarán cuando
se modifiquen las entidades o sus relaciones.

## Estructura del proyecto

La estructura actual del repositorio es la siguiente:

    .
    ├── analisis_bioquimico/
    │   ├── migrations/
    │   │   └── 0001_initial.py
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── tests.py
    │   └── views.py
    │
    ├── config/
    │   ├── __init__.py
    │   ├── asgi.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    │
    ├── docs/
    │   ├── diagramaER.mmd
    │   └── diagramaUML.mmd
    │
    ├── .gitignore
    ├── db.sqlite3
    ├── manage.py
    └── requirements.txt

### Descripción de los archivos y directorios

- `analisis_bioquimico/`: aplicación principal del sistema.
- `analisis_bioquimico/models.py`: definición de los modelos de datos.
- `analisis_bioquimico/views.py`: lugar donde se implementará la lógica
  de las vistas.
- `analisis_bioquimico/admin.py`: configuración del administrador de Django.
- `analisis_bioquimico/tests.py`: pruebas automatizadas de la aplicación.
- `analisis_bioquimico/migrations/`: migraciones de los modelos.
- `config/`: configuración general del proyecto Django.
- `config/settings.py`: configuración de aplicaciones, base de datos y otros
  componentes del proyecto.
- `config/urls.py`: configuración de las rutas principales.
- `docs/`: diagramas y documentación del diseño.
- `manage.py`: herramienta para ejecutar comandos administrativos de Django.
- `requirements.txt`: dependencias necesarias para el proyecto.
- `db.sqlite3`: archivo de base de datos SQLite utilizado en desarrollo.

## Instalación y ejecución

### Requisitos previos

- Python instalado.
- Git, si se desea clonar el repositorio.
- Una terminal compatible con los comandos indicados.

### 1. Clonar el repositorio

    git clone https://github.com/Villada-PG3/trabajo-practico-integrador-laboratorio_analisis_bioquimico.git
    cd trabajo-practico-integrador-laboratorio_analisis_bioquimico

Si ya se dispone del proyecto localmente, se puede omitir este paso.

### 2. Crear un entorno virtual

    python -m venv .venv

### 3. Activar el entorno virtual

En Windows, utilizando CMD:

    .venv\Scripts\activate

En Windows, utilizando PowerShell:

    .venv\Scripts\Activate.ps1

En Linux o macOS:

    source .venv/bin/activate

### 4. Instalar las dependencias

    python -m pip install -r requirements.txt

### 5. Aplicar las migraciones

    python manage.py migrate

Si se incorporan o modifican modelos y sus cambios todavía no tienen
una migración generada, ejecutar primero:

    python manage.py makemigrations

Y luego:

    python manage.py migrate

### 6. Iniciar el servidor de desarrollo

    python manage.py runserver

Django iniciará el servidor de desarrollo, normalmente disponible en:

http://127.0.0.1:8000/

Las páginas y funcionalidades disponibles dependerán de las vistas y rutas
que se hayan implementado.

## Base de datos

Durante el desarrollo se utiliza SQLite.

La configuración de la base de datos se encuentra en `config/settings.py`
y el archivo local se denomina `db.sqlite3`.

Django utiliza migraciones para reflejar los cambios de los modelos en la
estructura de la base de datos.

Cuando se agreguen, eliminen o modifiquen campos o modelos, será necesario
revisar y aplicar las migraciones correspondientes.

## Estado actual del proyecto

El proyecto se encuentra en una etapa inicial de desarrollo.

Actualmente:

- Está creada la estructura base del proyecto Django.
- Está creada la aplicación `analisis_bioquimico`.
- Están definidos los modelos principales del dominio.
- Está configurada una base de datos SQLite.
- Se dispone de una migración inicial.
- Se encuentran los diagramas ER y UML en la carpeta `docs/`.

Pendiente de desarrollo:

- Configuración de las rutas y las vistas.
- Implementación de las operaciones de consulta, creación, modificación
  y eliminación que correspondan.
- Configuración del administrador de Django.
- Desarrollo de las interfaces de usuario.
- Implementación de las reglas de negocio y validaciones.
- Gestión de los estados y las transiciones de las solicitudes.
- Implementación de la autenticación y los permisos según los roles.
- Validación de matrículas profesionales mediante el servicio externo previsto.
- Envío de correos electrónicos y notificaciones.
- Consulta de resultados por parte de los pacientes.
- Generación de reportes estadísticos.
- Pruebas automatizadas de las funcionalidades.

Esta lista se actualizará a medida que se incorporen nuevas funcionalidades.

## Documentación

Los diagramas del sistema se encuentran en la carpeta `docs/`.

Los archivos `.mmd` contienen los diagramas en formato Mermaid y pueden
visualizarse con herramientas compatibles con este formato.
