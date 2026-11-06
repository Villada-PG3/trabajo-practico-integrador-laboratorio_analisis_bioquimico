from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponseForbidden


def solo_responsable(view_func):
    """
    Permite acceder únicamente a usuarios
    autenticados con el rol Responsable de Análisis.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            messages.warning(
                request,
                'Debe iniciar sesión para acceder.'
            )
            return redirect('analisis_bioquimico:login')

        if not hasattr(request.user, 'responsable_analisis'):
            return HttpResponseForbidden(
                'No tiene permisos para acceder a esta función.'
            )

        return view_func(request, *args, **kwargs)

    return wrapper