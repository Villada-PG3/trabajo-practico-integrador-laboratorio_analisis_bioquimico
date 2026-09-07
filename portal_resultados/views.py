from django.shortcuts import render, redirect
from django.contrib import messages


# DATOS DE PRUEBA
# Más adelante los reemplazamos por datos de la base de datos.

PACIENTE_DEMO = {
    "dni": "47821688",
    "nombre": "Gino",
}


CAP_DEMO = "123"


SOLICITUDES_DEMO = [
    {
        "id": 1,
        "fecha": "05/09/2026",
        "estado": "Finalizada",
    },
    {
        "id": 2,
        "fecha": "01/09/2026",
        "estado": "Finalizada",
    },
]


RESULTADOS_DEMO = {
    1: [
        {
            "estudio": "Glucemia",
            "unidad": "mg/dL",
            "tecnica": "Enzimática",
            "valor": "92",
        },
        {
            "estudio": "Uremia",
            "unidad": "mg/dL",
            "tecnica": "UV",
            "valor": "31",
        },
        {
            "estudio": "Colesterol",
            "unidad": "mg/dL",
            "tecnica": "Enzimática",
            "valor": "180",
        },
    ],

    2: [
        {
            "estudio": "Glucemia",
            "unidad": "mg/dL",
            "tecnica": "Enzimática",
            "valor": "88",
        },
        {
            "estudio": "Uremia",
            "unidad": "mg/dL",
            "tecnica": "UV",
            "valor": "29",
        },
    ],
}


def login_view(request):

    if request.method == "POST":

        dni = request.POST.get("dni")
        cap = request.POST.get("cap")

        if dni == PACIENTE_DEMO["dni"] and cap == CAP_DEMO:

            request.session["paciente_dni"] = dni

            return redirect("historial")

        messages.error(
            request,
            "DNI o CAP incorrectos."
        )

    return render(request, "login.html")


def historial(request):

    if "paciente_dni" not in request.session:
        return redirect("login")

    contexto = {
        "paciente": PACIENTE_DEMO,
        "solicitudes": SOLICITUDES_DEMO,
    }

    return render(
        request,
        "historial.html",
        contexto
    )


def resultados(request, solicitud_id):

    if "paciente_dni" not in request.session:
        return redirect("login")

    resultados = RESULTADOS_DEMO.get(
        solicitud_id,
        []
    )

    contexto = {
        "paciente": PACIENTE_DEMO,
        "solicitud_id": solicitud_id,
        "resultados": resultados,
    }

    return render(
        request,
        "resultados.html",
        contexto
    )


def reportes(request):

    if "paciente_dni" not in request.session:
        return redirect("login")

    datos = {
        "enero": 10,
        "febrero": 15,
        "marzo": 20,
        "abril": 13,
        "mayo": 25,
        "junio": 18,
    }

    contexto = {
        "datos": datos,
    }

    return render(
        request,
        "reportes.html",
        contexto
    )


def logout_view(request):

    request.session.flush()

    return redirect("login")