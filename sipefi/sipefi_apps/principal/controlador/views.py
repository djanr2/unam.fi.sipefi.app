'''
    Este archivo funciona para conectar al modelo con el controlador y asi poder dar 
    respuesta a la peticion solicitada al servidor desde el cliente.
''' 
from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as conBD

from django.http import JsonResponse
from django.views.decorators.cache import never_cache


@never_cache
def cerrarSesionUsuarioSistema(request):
    """
        La funcion sirve para conectar la peticion cliente - servidor, 
        en este caso sirve para procesar el cerrado de la sesion del usuario logueado
    """
    token = request.POST.get('token','')
    resp = conBD().validaSesionUsuario(token, 2)
    if resp != "E":
        conBD().cierraSesionUsuario(token, "", 1)
    return JsonResponse({"resp": "OK" }) 