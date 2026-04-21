# -*- coding: utf-8 -*-
'''
    Este archivo funciona para conectar al modelo con el controlador y asi poder dar 
    respuesta a la peticion solicitada al servidor desde el cliente.
'''
from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as CBD

from django.http import JsonResponse
from django.views.decorators.cache import never_cache

from django.views import View
from django.views.generic import TemplateView
from django.shortcuts import render, redirect
from django.contrib import messages

from collections import OrderedDict


SESION_SIPEFI_KEYS = [
    "sipefi_id_usuario",
    "sipefi_usuario",
    "sipefi_nombre",
    "sipefi_token",
    "sipefi_roles",
    "sipefi_rol_activo_id",
    "sipefi_rol_activo_nombre",
]

def construir_meta_rol(rol_item):
    nombre_rol = str(rol_item.get("rol", "")).strip()
    id_rol = rol_item.get("id")

    tipo = "Perfil"
    division = "General"
    descripcion = "Acceso al sistema con el perfil seleccionado."
    resumen = "Perfil general"
    alcance = "Consulta y operación según permisos asignados."
    icono = "fa-solid fa-user-shield"
    badge_class = "badge bg-secondary-subtle text-secondary-emphasis"
    categoria_key = "otros"
    categoria_nombre = "Otros"
    orden_categoria = 9
    orden_tipo = 9

    # ===== Administración =====
    if nombre_rol == "Administrador":
        tipo = "Administrador"
        division = "Sistema"
        descripcion = "Acceso integral para administración, seguimiento y configuración general del sistema."
        resumen = "Administración global"
        alcance = "Puede operar transversalmente sobre todo el sistema."
        icono = "fa-solid fa-crown"
        badge_class = "badge bg-dark text-white"
        categoria_key = "administracion"
        categoria_nombre = "Administración"
        orden_categoria = 0
        orden_tipo = 0

    elif nombre_rol == "Operador Admin":
        tipo = "Operador Admin"
        division = "Sistema"
        descripcion = "Puede visualizar, editar y crear solicitudes de cualquier área del sistema."
        resumen = "Operación global"
        alcance = "Opera solicitudes de todas las divisiones."
        icono = "fa-solid fa-user-gear"
        badge_class = "badge bg-primary text-white"
        categoria_key = "administracion"
        categoria_nombre = "Administración"
        orden_categoria = 0
        orden_tipo = 1

    elif nombre_rol == "Validador Admin":
        tipo = "Validador Admin"
        division = "Sistema"
        descripcion = "Puede validar o rechazar cualquier solicitud en proceso dentro del sistema."
        resumen = "Validación global"
        alcance = "Valida solicitudes de todas las divisiones."
        icono = "fa-solid fa-user-check"
        badge_class = "badge bg-success text-white"
        categoria_key = "administracion"
        categoria_nombre = "Administración"
        orden_categoria = 0
        orden_tipo = 2

    # ===== Operación =====
    elif nombre_rol.startswith("Operador "):
        division = nombre_rol.replace("Operador ", "", 1).strip()
        tipo = "Operador"
        descripcion = f"Captura, edición y seguimiento operativo de solicitudes para {division}."
        resumen = "Captura y gestión operativa"
        alcance = f"Opera solicitudes asociadas a {division}."
        icono = "fa-solid fa-pen-to-square"
        badge_class = "badge bg-primary-subtle text-primary-emphasis"
        categoria_key = "operacion"
        categoria_nombre = "Operación"
        orden_categoria = 1
        orden_tipo = 1

    # ===== Validación =====
    elif nombre_rol.startswith("Validador "):
        division = nombre_rol.replace("Validador ", "", 1).strip()
        tipo = "Validador"
        descripcion = f"Revisión, validación y seguimiento de solicitudes para {division}."
        resumen = "Revisión y validación"
        alcance = f"Valida solicitudes asociadas a {division}."
        icono = "fa-solid fa-clipboard-check"
        badge_class = "badge bg-success-subtle text-success-emphasis"
        categoria_key = "validacion"
        categoria_nombre = "Validación"
        orden_categoria = 2
        orden_tipo = 2

    # ===== Coordinación =====
    elif nombre_rol.startswith("Coordinador "):
        division = nombre_rol.replace("Coordinador ", "", 1).strip()
        tipo = "Coordinador"
        descripcion = f"Consulta y descarga de documentos PDF para la coordinación de {division}."
        resumen = "Consulta y descarga"
        alcance = f"Acceso orientado a consulta documental de {division}."
        icono = "fa-solid fa-user-tie"
        badge_class = "badge bg-warning-subtle text-warning-emphasis"
        categoria_key = "coordinacion"
        categoria_nombre = "Coordinación"
        orden_categoria = 3
        orden_tipo = 3

    search_text = f"{nombre_rol} {tipo} {division} {descripcion} {resumen} {categoria_nombre}".lower()

    return {
        "id": id_rol,
        "rol": nombre_rol,
        "tipo": tipo,
        "division": division,
        "descripcion": descripcion,
        "resumen": resumen,
        "alcance": alcance,
        "icono": icono,
        "badge_class": badge_class,
        "categoria_key": categoria_key,
        "categoria_nombre": categoria_nombre,
        "orden_categoria": orden_categoria,
        "orden_tipo": orden_tipo,
        "search_text": search_text,
    }

def construir_roles_ui(roles):
    roles_ui = [construir_meta_rol(r) for r in roles]

    roles_ui.sort(
        key=lambda r: (
            r["orden_categoria"],
            r["division"].lower(),
            r["orden_tipo"],
            r["rol"].lower()
        )
    )

    stats = {
        "total": len(roles_ui),
        "administracion": 0,
        "operacion": 0,
        "validacion": 0,
        "coordinacion": 0,
        "otros": 0,
    }

    for rol in roles_ui:
        key = rol["categoria_key"]
        if key in stats:
            stats[key] += 1
        else:
            stats["otros"] += 1

    filtros = [
        {"key": "all", "label": "Todos", "total": stats["total"]},
        {"key": "administracion", "label": "Administración", "total": stats["administracion"]},
        {"key": "operacion", "label": "Operación", "total": stats["operacion"]},
        {"key": "validacion", "label": "Validación", "total": stats["validacion"]},
        {"key": "coordinacion", "label": "Coordinación", "total": stats["coordinacion"]},
    ]

    return {
        "roles_ui": roles_ui,
        "rol_preseleccionado": roles_ui[0] if roles_ui else None,
        "stats": stats,
        "filtros": filtros,
    }
    
def es_dupla_operador_validador(roles):
    """
    Detecta si el usuario solo tiene dos perfiles y corresponden
    a la dupla Operador + Validador de la misma división.
    """
    if len(roles) != 2:
        return False

    nombres = sorted([str(r.get("rol", "")).strip() for r in roles])

    if not nombres[0].startswith("Operador "):
        return False

    if not nombres[1].startswith("Validador "):
        return False

    division_operador = nombres[0].replace("Operador ", "", 1).strip()
    division_validador = nombres[1].replace("Validador ", "", 1).strip()

    return division_operador == division_validador

def limpiar_sesion_sipefi(request):
    for key in SESION_SIPEFI_KEYS:
        request.session.pop(key, None)


def redireccion_sesion_activa(request):
    token = request.session.get("sipefi_token", "")
    roles = request.session.get("sipefi_roles", [])
    rol_activo_id = request.session.get("sipefi_rol_activo_id")

    if not token:
        return None

    if CBD().validaSesionUsuario(token, 1) != "OK":
        limpiar_sesion_sipefi(request)
        return None

    if rol_activo_id:
        return redirect("/SIPEFI/Tomo_II")

    if len(roles) > 1:
        return redirect("/SIPEFI/seleccion-perfil/")

    if len(roles) == 1:
        request.session["sipefi_rol_activo_id"] = roles[0]["id"]
        request.session["sipefi_rol_activo_nombre"] = roles[0]["rol"]
        return redirect("/SIPEFI/Tomo_II")

    limpiar_sesion_sipefi(request)
    return None


class LoginSipefi(View):

    def get(self, request):
        redir = redireccion_sesion_activa(request)
        if redir:
            return redir
        return render(request, 'principal/login.html')

    def post(self, request):
        usuario = request.POST.get('usuario', '').strip()
        clave = request.POST.get('clave', '').strip()

        limpiar_sesion_sipefi(request)

        resultado = CBD().validar_credenciales(usuario, clave)

        if not resultado:
            messages.error(request, 'Usuario o contraseña inválidos.')
            return render(request, 'principal/login.html')

        id_usuario = resultado["usuario"]["id"]
        usuario_sistema = resultado["usuario"]["usuario_sistema"]
        nombre = resultado["usuario"]["nombre"]
        id_perfil_base = resultado["usuario"]["id_perfil"]
        token = resultado["token"]

        roles = CBD().mapeoRolUsuario(id_perfil_base)

        if roles.get("estatus") != 200 or not roles.get("resp"):
            CBD().cierraSesionUsuario(token, "", 1)
            messages.error(request, 'No fue posible determinar los perfiles del usuario.')
            return render(request, 'principal/login.html')

        # Cerramos cualquier otro token previo del mismo usuario
        CBD().cierraSesionUsuario(token, id_usuario, 2)

        request.session["sipefi_id_usuario"] = id_usuario
        request.session["sipefi_usuario"] = usuario_sistema
        request.session["sipefi_nombre"] = nombre
        request.session["sipefi_token"] = token
        request.session["sipefi_roles"] = roles["resp"]

        if len(roles["resp"]) == 1:
            request.session["sipefi_rol_activo_id"] = roles["resp"][0]["id"]
            request.session["sipefi_rol_activo_nombre"] = roles["resp"][0]["rol"]
            return redirect("/SIPEFI/Tomo_II")

        request.session.pop("sipefi_rol_activo_id", None)
        request.session.pop("sipefi_rol_activo_nombre", None)
        return redirect("/SIPEFI/seleccion-perfil/")


class SeleccionPerfilView(TemplateView):
    template_name = "principal/seleccion_perfil.html"

    def get(self, request, *args, **kwargs):
        token = request.session.get("sipefi_token", "")
        roles = request.session.get("sipefi_roles", [])

        if not token or CBD().validaSesionUsuario(token, 1) != "OK":
            limpiar_sesion_sipefi(request)
            return redirect("/SIPEFI/login/")

        if not roles:
            limpiar_sesion_sipefi(request)
            return redirect("/SIPEFI/login/")

        if len(roles) == 1:
            request.session["sipefi_rol_activo_id"] = roles[0]["id"]
            request.session["sipefi_rol_activo_nombre"] = roles[0]["rol"]
            return redirect("/SIPEFI/Tomo_II")

        contexto = {
            "usuario": request.session.get("sipefi_usuario", ""),
            "nombre": request.session.get("sipefi_nombre", ""),
        }
        
        contexto.update(construir_roles_ui(roles))
        contexto["modo_simple_dupla"] = es_dupla_operador_validador(roles)
        
        return render(request, self.template_name, contexto)


@never_cache
def seleccionarPerfilActivo(request):
    if request.method != "POST":
        return redirect("/SIPEFI/seleccion-perfil/")

    token = request.session.get("sipefi_token", "")
    roles = request.session.get("sipefi_roles", [])

    if not token or CBD().validaSesionUsuario(token, 1) != "OK":
        limpiar_sesion_sipefi(request)
        return redirect("/SIPEFI/login/")

    try:
        id_perfil = int(request.POST.get("id_perfil", "0"))
    except ValueError:
        messages.error(request, "Perfil inválido.")
        return redirect("/SIPEFI/seleccion-perfil/")

    perfil_seleccionado = next((r for r in roles if int(r["id"]) == id_perfil), None)

    if not perfil_seleccionado:
        messages.error(request, "El perfil seleccionado no es válido para este usuario.")
        return redirect("/SIPEFI/seleccion-perfil/")

    request.session["sipefi_rol_activo_id"] = perfil_seleccionado["id"]
    request.session["sipefi_rol_activo_nombre"] = perfil_seleccionado["rol"]

    return redirect("/SIPEFI/Tomo_II")


@never_cache
def logoutSipefi(request):
    token = request.session.get("sipefi_token", "")
    if token:
        CBD().cierraSesionUsuario(token, "", 1)

    request.session.flush()
    return redirect("/SIPEFI/login/")


@never_cache
def cerrarSesionUsuarioSistema(request):
    """
        Compatibilidad con el flujo anterior.
        Si algún proceso viejo lo llama, cerramos token y sesión.
    """
    token = request.POST.get('token', '') or request.session.get("sipefi_token", "")

    if token:
        resp = CBD().validaSesionUsuario(token, 2)
        if resp != "I":
            CBD().cierraSesionUsuario(token, "", 1)

    limpiar_sesion_sipefi(request)
    return JsonResponse({"resp": "OK"})