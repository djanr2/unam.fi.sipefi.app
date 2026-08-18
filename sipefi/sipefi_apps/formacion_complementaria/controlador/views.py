# -*- coding: utf-8 -*-
import json
import logging
import uuid

from django.conf import settings
from django.db import transaction
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from sipefi_apps.formacion_complementaria.modelo.excepciones import FormacionComplementariaError
from sipefi_apps.formacion_complementaria.servicio.formacion_service import FormacionComplementariaService
from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as ConsultasTomoII

logger = logging.getLogger(__name__)


def _referencia_error():
    return uuid.uuid4().hex[:12].upper()


def _es_coordinador(request):
    nombre = str(request.session.get("sipefi_rol_activo_nombre", "")).strip()
    return nombre.lower().startswith("coordinador")


def _identidad(request):
    id_usuario = request.session.get("sipefi_id_usuario")
    usuario = str(request.session.get("sipefi_usuario", "")).strip()
    token = str(request.session.get("sipefi_token", "")).strip()
    if not id_usuario or not usuario or not token:
        raise FormacionComplementariaError(401, "La sesión no es válida.")
    if not _es_coordinador(request):
        raise FormacionComplementariaError(
            403,
            "El módulo de Formación complementaria es exclusivo para el perfil Coordinador.",
        )
    return int(id_usuario), usuario


def _leer_json(request):
    if request.method != "POST":
        raise FormacionComplementariaError(405, "Método no permitido.")
    raw = request.POST.get("obj")
    if not raw:
        raise FormacionComplementariaError(400, "No se recibieron datos para procesar.")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FormacionComplementariaError(400, "Los datos recibidos no son JSON válido.") from exc


def _respuesta_endpoint(funcion):
    def wrapper(request, *args, **kwargs):
        try:
            return funcion(request, *args, **kwargs)
        except FormacionComplementariaError as exc:
            return JsonResponse(
                {"estatus": exc.status_code, "error": exc.user_message},
                status=exc.status_code,
            )
        except Exception:
            referencia = _referencia_error()
            logger.exception(
                "Error no controlado en Formación complementaria. Referencia=%s",
                referencia,
            )
            return JsonResponse(
                {
                    "estatus": 500,
                    "error": "No fue posible completar la operación.",
                    "referencia": referencia,
                },
                status=500,
            )
    return wrapper


@method_decorator(never_cache, name="dispatch")
class VistaFormacionComplementaria(TemplateView):
    template_name = "formacion_complementaria/index.html"

    def get(self, request, *args, **kwargs):
        token = request.session.get("sipefi_token", "")
        usuario = request.session.get("sipefi_usuario", "")
        if not token or not usuario:
            request.session.flush()
            return redirect("/SIPEFI/login/")
        if ConsultasTomoII().validaSesionUsuario(token, 1) != "OK":
            request.session.flush()
            return redirect("/SIPEFI/login/")
        if not _es_coordinador(request):
            return HttpResponseForbidden(
                "El módulo de Formación complementaria es exclusivo para el perfil Coordinador."
            )

        roles = request.session.get("sipefi_roles", [])
        contexto = {
            "usuario": usuario,
            "rol": request.session.get("sipefi_rol_activo_id", ""),
            "rol_nombre": request.session.get("sipefi_rol_activo_nombre", ""),
            "static_version": settings.STATIC_VERSION,
            "tiene_multiples_roles": len(roles) > 1,
        }
        return TemplateResponse(request, self.template_name, contexto)


@_respuesta_endpoint
def datos_iniciales(request):
    id_usuario, _ = _identidad(request)
    if request.method != "POST":
        raise FormacionComplementariaError(405, "Método no permitido.")
    return JsonResponse(
        {"estatus": 200, "datos": FormacionComplementariaService().datos_iniciales(id_usuario)}
    )


@_respuesta_endpoint
def listar(request):
    id_usuario, _ = _identidad(request)
    if request.method != "POST":
        raise FormacionComplementariaError(405, "Método no permitido.")
    return JsonResponse(
        {"estatus": 200, "solicitudes": FormacionComplementariaService().listar(id_usuario)}
    )


@_respuesta_endpoint
def asignaturas_disponibles(request):
    id_usuario, _ = _identidad(request)
    datos = _leer_json(request)
    id_formacion = datos.get("idFormacion")
    return JsonResponse(
        {
            "estatus": 200,
            "asignaturas": FormacionComplementariaService().asignaturas(id_formacion, id_usuario),
        }
    )


@_respuesta_endpoint
def bibliografias_apoyo(request):
    id_usuario, _ = _identidad(request)
    datos = _leer_json(request)
    id_solicitud = datos.get("idSolicitudApoyo")
    if not id_solicitud:
        raise FormacionComplementariaError(400, "Seleccione una asignatura de apoyo.")
    return JsonResponse(
        {
            "estatus": 200,
            "bibliografias": FormacionComplementariaService().bibliografias(
                id_solicitud, datos.get("idFormacion"), id_usuario
            ),
        }
    )


@_respuesta_endpoint
def detalle(request):
    id_usuario, _ = _identidad(request)
    datos = _leer_json(request)
    id_formacion = datos.get("idFormacion")
    if not id_formacion:
        raise FormacionComplementariaError(400, "El folio solicitado no es válido.")
    return JsonResponse(
        {
            "estatus": 200,
            "detalle": FormacionComplementariaService().detalle(id_formacion, id_usuario),
        }
    )


@_respuesta_endpoint
def guardar(request):
    id_usuario, usuario = _identidad(request)
    payload = _leer_json(request)
    with transaction.atomic():
        resultado = FormacionComplementariaService().guardar(
            payload, id_usuario, usuario, completar=False
        )
    return JsonResponse({"estatus": 200, "resultado": resultado})


@_respuesta_endpoint
def completar(request):
    id_usuario, usuario = _identidad(request)
    payload = _leer_json(request)
    with transaction.atomic():
        resultado = FormacionComplementariaService().guardar(
            payload, id_usuario, usuario, completar=True
        )
    return JsonResponse({"estatus": 200, "resultado": resultado})
