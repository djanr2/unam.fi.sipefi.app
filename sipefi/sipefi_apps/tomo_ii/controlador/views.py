# -*- coding: utf-8 -*-
"""
    Este archivo funciona para conectar al modelo con el controlador y asi poder dar
    respuesta a la peticion solicitada al servidor desde el cliente.
"""

from django.template.response import TemplateResponse
from django.http import JsonResponse
from django.views.decorators.cache import never_cache
from django.db import transaction
from django.conf import settings
import json
import logging
import uuid

from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as CBD
from sipefi_apps.tomo_ii.modelo.Solicitud import Solicitud
from sipefi_apps.tomo_ii.modelo.excepciones import SolicitudError

logger = logging.getLogger(__name__)

from django.views.generic import TemplateView
from django.shortcuts import redirect


def _extraer_error_controlado(exc):
    if isinstance(exc, SolicitudError):
        return exc.status_code, exc.user_message

    # Compatibilidad con excepciones funcionales históricas.
    if exc.args and isinstance(exc.args[0], tuple) and len(exc.args[0]) == 2:
        code, message = exc.args[0]
        if isinstance(code, int) and 400 <= code < 500:
            return code, str(message)

    return None


def _referencia_error():
    return uuid.uuid4().hex[:12].upper()


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
        context['static_version'] = settings.STATIC_VERSION
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
    try:
        return JsonResponse(CBD().buscaSolicitudesUsuario(usuario, rol))
    except Exception:
        referencia = _referencia_error()
        logger.exception("Error al consultar tablas de solicitudes. Referencia=%s", referencia)
        return JsonResponse({
            "estatusTSU": 500,
            "estatusTSA": 500,
            "estatusTSR": 500,
            "error": "No fue posible consultar las solicitudes.",
            "referencia": referencia,
        }, status=500)


def requestRecargaPagina(request):
    """
        Se mantiene por compatibilidad.
    """
    token = request.session.get("sipefi_token", "") or request.POST.get('token', '')
    if token:
        CBD().actualizaEstatusToken(token)
    return JsonResponse({"resp": "OK"})


@never_cache
def requestAccionSolicitud(request):
    """
    Vista que procesa la solicitud recibida del frontend en formato de formulario con JSON serializado.
    """
    if request.method != "POST":
        return JsonResponse({"estatus": 405, "error": "Método no permitido"}, status=405)

    try:
        obj_json = request.POST.get("obj")
        if not obj_json:
            return JsonResponse({"estatus": 400, "error": "No se recibió el parámetro 'obj'"}, status=400)

        datos = json.loads(obj_json)

        # La identidad y el perfil activo se obtienen de la sesion del servidor.
        # No se confia en usuario/rol/token enviados desde JavaScript.
        usuario_sesion = request.session.get("sipefi_usuario", "")
        rol_sesion = request.session.get("sipefi_rol_activo_id")
        token_sesion = request.session.get("sipefi_token", "")
        if not usuario_sesion or not rol_sesion or not token_sesion:
            return JsonResponse({"estatus": 401, "error": "Sesion no valida."}, status=401)

        metadatos = datos.setdefault("metadatos", {})
        metadatos["usuario"] = usuario_sesion
        metadatos["usuarioSoli"] = usuario_sesion
        metadatos["rol"] = rol_sesion
        metadatos["token"] = token_sesion

        with transaction.atomic():
            procesador = Solicitud()
            resultado = procesador.procesar(datos)

        return JsonResponse({"estatus": 200, "respuesta": resultado})

    except json.JSONDecodeError:
        return JsonResponse({"estatus": 400, "error": "El contenido del campo 'obj' no es JSON válido."}, status=400)

    except Exception as e:
        controlado = _extraer_error_controlado(e)
        if controlado:
            status, message = controlado
            return JsonResponse(
                {"estatus": status, "code": status, "error": message},
                status=status,
            )

        referencia = _referencia_error()
        logger.exception("Error al procesar una solicitud. Referencia=%s", referencia)
        return JsonResponse({
            "estatus": 500,
            "code": 500,
            "error": "No fue posible procesar la solicitud.",
            "referencia": referencia,
        }, status=500)
    

def requestCargaSolicitud(request):
    """
        Obtiene los datos de la solicitud deseada por el usuario.
    """
    accion = request.POST.get('action', '')
    infoBusqueda = request.POST.get('info', '')
    obj = infoBusqueda.split("#@@#")

    if len(obj) < 2 or not obj[0].isdigit() or not obj[1].isdigit():
        return JsonResponse(
            {"estatus": 400, "error": "Los datos de la solicitud son inválidos."},
            status=400,
        )

    try:
        return JsonResponse(Solicitud().dameDatosSolicitud(obj[0], obj[1], accion))
    except Exception:
        referencia = _referencia_error()
        logger.exception("Error al cargar una solicitud. Referencia=%s", referencia)
        return JsonResponse({
            "estatus": 500,
            "error": "No fue posible cargar la solicitud.",
            "referencia": referencia,
        }, status=500)


def requestCancelarSol(request):
    """
        Cancela una solicitud.
    """
    if request.method != "POST":
        return JsonResponse(
            {"ok": False, "code": 405, "error": "Método no permitido."},
            status=405,
        )

    try:
        raw = request.POST.get("obj")
        if not raw:
            return JsonResponse(
                {"ok": False, "code": 400, "error": "No se recibieron los datos de cancelación."},
                status=400,
            )

        obj = json.loads(raw)
        idSol = obj["numSoli"]
        idEst = obj["estatus"]
        token = request.session.get("sipefi_token", "")
        rol = request.session.get("sipefi_rol_activo_id", "")
        usuario = request.session.get("sipefi_usuario", "")
        comentario = obj["comentario"]

        if not token or not rol or not usuario:
            return JsonResponse({"ok": False, "code": 401, "error": "Sesion no valida."}, status=401)

        with transaction.atomic():
            resp = Solicitud().cancelaSolicitud(idSol, idEst, token, rol, usuario, comentario)

        return JsonResponse({"ok": True, "code": 200, "data": resp}, status=200)

    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return JsonResponse(
            {"ok": False, "code": 400, "error": "Los datos de cancelación son inválidos."},
            status=400,
        )

    except Exception as e:
        controlado = _extraer_error_controlado(e)
        if controlado:
            status, message = controlado
            return JsonResponse(
                {"ok": False, "code": status, "estatus": status, "error": message},
                status=status,
            )

        referencia = _referencia_error()
        logger.exception("Error al cancelar una solicitud. Referencia=%s", referencia)
        return JsonResponse({
            "ok": False,
            "code": 500,
            "estatus": 500,
            "error": "No fue posible cancelar la solicitud.",
            "referencia": referencia,
        }, status=500)