# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation

from sipefi_apps.formacion_complementaria.modelo.excepciones import FormacionComplementariaError


def texto(valor, *, max_length=None):
    resultado = "" if valor is None else str(valor).strip()
    if max_length and len(resultado) > max_length:
        raise FormacionComplementariaError(
            400,
            f"Uno de los textos excede la longitud máxima permitida ({max_length} caracteres).",
        )
    return resultado


def entero_opcional(valor, nombre, *, minimo=None, maximo=None):
    if valor in (None, ""):
        return None
    try:
        numero = int(valor)
    except (TypeError, ValueError) as exc:
        raise FormacionComplementariaError(400, f"El campo {nombre} no es válido.") from exc
    if minimo is not None and numero < minimo:
        raise FormacionComplementariaError(400, f"El campo {nombre} debe ser mayor o igual a {minimo}.")
    if maximo is not None and numero > maximo:
        raise FormacionComplementariaError(400, f"El campo {nombre} debe ser menor o igual a {maximo}.")
    return numero


def entero_requerido(valor, nombre, *, minimo=None, maximo=None):
    numero = entero_opcional(valor, nombre, minimo=minimo, maximo=maximo)
    if numero is None:
        raise FormacionComplementariaError(400, f"El campo {nombre} es obligatorio.")
    return numero


def decimal_opcional(valor, nombre, *, minimo=Decimal("0")):
    if valor in (None, ""):
        return None
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise FormacionComplementariaError(400, f"El campo {nombre} no es válido.") from exc
    if minimo is not None and numero < minimo:
        raise FormacionComplementariaError(400, f"El campo {nombre} no puede ser negativo.")
    return numero


def lista(valor, nombre):
    if valor is None:
        return []
    if not isinstance(valor, list):
        raise FormacionComplementariaError(400, f"La sección {nombre} no tiene el formato esperado.")
    return valor


def validar_payload_base(payload):
    if not isinstance(payload, dict):
        raise FormacionComplementariaError(400, "Los datos recibidos no tienen el formato esperado.")

    secciones = ("datosGenerales", "temas", "bibliografias", "estrategias")
    faltantes = [seccion for seccion in secciones if seccion not in payload]
    if faltantes:
        raise FormacionComplementariaError(
            400,
            "La información no terminó de cargarse. Actualiza la pantalla antes de guardar.",
        )

    if payload.get("cargaCompleta") is not True:
        raise FormacionComplementariaError(
            400,
            "La información no terminó de cargarse. Actualiza la pantalla antes de guardar.",
        )
