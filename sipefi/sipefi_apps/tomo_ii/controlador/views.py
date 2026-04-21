# -*- coding: utf-8 -*-
"""
    Este archivo funciona para conectar al modelo con el controlador y asi poder dar
    respuesta a la peticion solicitada al servidor desde el cliente.
"""

from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json

from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as CBD
from sipefi_apps.tomo_ii.modelo.Solicitud import Solicitud

from django.views.generic import TemplateView
from django.shortcuts import redirect


class Vista_Principal_TomoII(TemplateView):
    """
        Clase en donde se hace uso de un TemplateView para mapear la url inicial del sistema.
    """
    def __init__(self):
        self.template_name = "tomo_ii/indexTomoII.html"
        self.usuario = ""
        self.rol = ""
        self.rol_nombre = ""
        self.urlSIPEFI = ""
        self.token = ""
        self.tiene_multiples_roles = False
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['idsValidador'] = CBD().buscaRolXNombre("Validador")
        context['usuario'] = self.usuario
        context['rol'] = self.rol
        context['rol_nombre'] = self.rol_nombre
        context['sipefi_login'] = self.urlSIPEFI
        context['token'] = self.token
        context['universo'] = 1
        context['tiene_multiples_roles'] = self.tiene_multiples_roles
        return context
    
    def get(self, request):
        token = request.session.get("sipefi_token", "")
        usuario = request.session.get("sipefi_usuario", "")
        roles = request.session.get("sipefi_roles", [])
        rol_id = request.session.get("sipefi_rol_activo_id")
        rol_nombre = request.session.get("sipefi_rol_activo_nombre", "")

        if not token or not usuario:
            request.session.flush()
            return redirect("/SIPEFI/login/")

        if CBD().validaSesionUsuario(token, 1) != "OK":
            request.session.flush()
            return redirect("/SIPEFI/login/")

        if not roles:
            request.session.flush()
            return redirect("/SIPEFI/login/")

        if not rol_id:
            if len(roles) == 1:
                request.session["sipefi_rol_activo_id"] = roles[0]["id"]
                request.session["sipefi_rol_activo_nombre"] = roles[0]["rol"]
                rol_id = roles[0]["id"]
                rol_nombre = roles[0]["rol"]
            else:
                return redirect("/SIPEFI/seleccion-perfil/")

        self.usuario = usuario
        self.rol = rol_id
        self.rol_nombre = rol_nombre
        self.urlSIPEFI = "/SIPEFI/logout/"
        self.token = token
        self.tiene_multiples_roles = len(roles) > 1

        return TemplateResponse(request, self.template_name, self.get_context_data())
 

def requestTablasSoli(request):
    """
        Consulta informacion de las solicitudes del usuario logueado.
    """
    usuario = request.session.get('sipefi_usuario', '')
    rol = request.session.get('sipefi_rol_activo_id', '')
    return JsonResponse(CBD().buscaSolicitudesUsuario(usuario, rol))


def requestRecargaPagina(request):
    """
        Se mantiene por compatibilidad.
    """
    token = request.session.get("sipefi_token", "") or request.POST.get('token', '')
    if token:
        CBD().actualizaEstatusToken(token)
    return JsonResponse({"resp": "OK"})


@never_cache
@csrf_exempt
def requestAccionSolicitud(request):
    """
    Vista que procesa la solicitud recibida del frontend en formato de formulario con JSON serializado.
    """
    if request.method != "POST":
        return JsonResponse({"estatus": 405, "error": "Método no permitido"})

    try:
        obj_json = request.POST.get("obj")
        if not obj_json:
            return JsonResponse({"estatus": 400, "error": "No se recibió el parámetro 'obj'"})

        datos = json.loads(obj_json)

        with transaction.atomic():
            procesador = Solicitud()
            resultado = procesador.procesar(datos)

        return JsonResponse({"estatus": 200, "respuesta": resultado})

    except json.JSONDecodeError:
        return JsonResponse({"estatus": 400, "error": "El contenido del campo 'obj' no es JSON válido."})

    except Exception as e:
        status = 500
        message = str(e)

        if e.args and isinstance(e.args[0], tuple) and len(e.args[0]) == 2:
            code, msg = e.args[0]
            if isinstance(code, int):
                status, message = code, msg

        return JsonResponse({"estatus": status, "error": message})
    

def requestCargaSolicitud(request):
    """
        Obtiene los datos de la solicitud deseada por el usuario.
    """
    accion = request.POST.get('action', '')
    infoBusqueda = request.POST.get('info', '')
    obj = infoBusqueda.split("#@@#")
    return JsonResponse(Solicitud().dameDatosSolicitud(obj[0], obj[1], accion))


def requestCancelarSol(request):
    """
        Cancela una solicitud.
    """
    try:
        raw = request.POST.get("obj")
        obj = json.loads(raw)

        idSol = obj["numSoli"]
        idEst = obj["estatus"]
        token = request.session.get("sipefi_token", "") or obj.get("token", "")
        rol = request.session.get("sipefi_rol_activo_id", "") or obj.get("rol", "")
        usuario = request.session.get("sipefi_usuario", "") or obj.get("usuario", "")
        comentario = obj["comentario"]

        with transaction.atomic():
            resp = Solicitud().cancelaSolicitud(idSol, idEst, token, rol, usuario, comentario)

        return JsonResponse({"ok": True, "code": 200, "data": resp}, status=200)

    except Exception as e:
        if e.args and isinstance(e.args[0], tuple) and e.args[0][0] == 409:
            _, msg = e.args[0]
            return JsonResponse({"ok": False, "code": 409, "error": msg}, status=409)

        return JsonResponse(
            {"ok": False, "code": 500, "error": str(e)},
            status=500
        )