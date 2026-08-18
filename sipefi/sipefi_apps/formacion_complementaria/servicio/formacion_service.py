# -*- coding: utf-8 -*-
import re

from django.db import IntegrityError

from sipefi_apps.formacion_complementaria.modelo.ConsultasBD import ConsultasBD
from sipefi_apps.formacion_complementaria.modelo.excepciones import FormacionComplementariaError
from sipefi_apps.formacion_complementaria.validadores.validaciones import (
    decimal_opcional,
    entero_opcional,
    entero_requerido,
    lista,
    texto,
    validar_payload_base,
)


class FormacionComplementariaService:
    ESTATUS_BORRADOR = 1
    ESTATUS_COMPLETADA = 2
    SEMANAS_SEMESTRE = 16
    TIPO_PRACTICO = 2
    CARACTER_OPTATIVO = 2
    MAX_JUSTIFICACION = 12000

    def __init__(self):
        self.db = ConsultasBD()

    def datos_iniciales(self, id_usuario):
        return {
            "catalogos": self.db.catalogos(),
            "asignaturas": self.db.asignaturas_disponibles(id_usuario),
            "solicitudes": self.db.listar_propias(id_usuario),
        }

    def listar(self, id_usuario):
        return self.db.listar_propias(id_usuario)

    def asignaturas(self, id_formacion=None, id_usuario=None):
        if id_formacion is not None:
            if id_usuario is None or not self.db.obtener_cabecera(id_formacion, id_usuario):
                raise FormacionComplementariaError(404, "No se encontró la formación complementaria solicitada.")
        return self.db.asignaturas_disponibles(id_usuario, id_formacion)

    @staticmethod
    def _normalizar_entero_respuesta(valor):
        """
        Convierte a int únicamente valores numéricos sin parte decimal.

        Ejemplos:
        Decimal("20.00") -> 20
        Decimal("30.00") -> 30
        Decimal("20.50") -> se conserva, no se trunca.
        """
        if valor is None:
            return None

        try:
            if valor == valor.to_integral_value():
                return int(valor)
            return valor
        except AttributeError:
            pass

        try:
            numero = float(valor)
        except (TypeError, ValueError):
            return valor

        return int(numero) if numero.is_integer() else valor

    def detalle(self, id_formacion, id_usuario):
        detalle = self.db.obtener_detalle(id_formacion, id_usuario)
        if not detalle:
            raise FormacionComplementariaError(404, "No se encontró la formación complementaria solicitada.")

        for campo in (
            "horas_pract_semana",
            "horas_pract_semestre",
        ):
            detalle[campo] = self._normalizar_entero_respuesta(detalle.get(campo))

        for tema in detalle.get("temas", []):
            tema["horas_tema"] = self._normalizar_entero_respuesta(
                tema.get("horas_tema")
            )

        detalle["bibliografias_disponibles"] = self.db.bibliografias_origen(
            detalle["id_solicitud_apoyo"], id_usuario, id_formacion
        )
        detalle["solo_lectura"] = int(detalle["id_estatus_fc"]) == self.ESTATUS_COMPLETADA
        return detalle

    def bibliografias(self, id_solicitud, id_formacion=None, id_usuario=None):
        if id_formacion is not None:
            cabecera = self.db.obtener_cabecera(id_formacion, id_usuario)
            if not cabecera:
                raise FormacionComplementariaError(404, "No se encontró la formación complementaria solicitada.")
            if int(cabecera["id_solicitud_apoyo"]) != int(id_solicitud):
                # Al cambiar la asignatura en un borrador no se deben recuperar copias del apoyo anterior.
                id_formacion = None
        apoyo = self.db.asignatura_apoyo_activa(id_solicitud, id_usuario)
        if not apoyo and id_formacion is None:
            raise FormacionComplementariaError(
                404,
                "La asignatura de apoyo debe pertenecer a la misma división del usuario, estar concluida, ser obligatoria y tener una clave válida de cuatro dígitos.",
            )
        return self.db.bibliografias_origen(id_solicitud, id_usuario, id_formacion)

    @staticmethod
    def _normalizar_nombre(prefijo, nombre_apoyo):
        prefijo = " ".join(str(prefijo).upper().split())
        nombre = " ".join(str(nombre_apoyo).upper().split())
        return f"{prefijo} {nombre}. FORMACIÓN COMPLEMENTARIA"

    @staticmethod
    def _clave_formacion(clave_subprograma, clave_apoyo):
        clave_apoyo = str(clave_apoyo or "").strip()
        if not re.fullmatch(r"\d{4}", clave_apoyo):
            raise FormacionComplementariaError(
                409,
                "La asignatura de apoyo debe contar con una clave numérica válida de exactamente cuatro dígitos.",
            )

        clave_subprograma = str(clave_subprograma or "").strip()
        if not re.fullmatch(r"\d{2}", clave_subprograma):
            raise FormacionComplementariaError(
                409,
                "La clave del subprograma no es válida.",
            )

        return f"21{clave_subprograma}{clave_apoyo}"

    @staticmethod
    def _hora_entera_opcional(valor, nombre):
        numero = decimal_opcional(valor, nombre)
        if numero is None:
            return None

        if numero != numero.to_integral_value():
            raise FormacionComplementariaError(
                400,
                f"El campo {nombre} debe ser un número entero; no se permiten decimales.",
            )

        return int(numero)

    def _preparar_temas(self, valor):
        temas_entrada = lista(valor, "Temario")
        temas = []
        numeros = set()
        for indice, item in enumerate(temas_entrada, start=1):
            if not isinstance(item, dict):
                raise FormacionComplementariaError(400, "Uno de los temas no tiene el formato esperado.")
            numero = entero_opcional(item.get("numTema"), "número de tema", minimo=1) or indice
            if numero in numeros:
                raise FormacionComplementariaError(400, "Existen números de tema duplicados.")
            numeros.add(numero)
            temas.append(
                {
                    "num_tema": numero,
                    "tema": texto(item.get("tema"), max_length=250),
                    "horas_tema": self._hora_entera_opcional(item.get("horas"), "horas del tema"),
                }
            )
        temas.sort(key=lambda item: item["num_tema"])
        for indice, tema in enumerate(temas, start=1):
            tema["num_tema"] = indice
        return temas

    def _preparar_ids_catalogo(self, valores, nombre, tabla, columna):
        resultado = []
        vistos = set()
        for valor in lista(valores, nombre):
            id_catalogo = entero_requerido(valor, nombre, minimo=1)
            if id_catalogo in vistos:
                continue
            if not self.db.existe_catalogo(tabla, columna, id_catalogo):
                raise FormacionComplementariaError(400, f"Una opción de {nombre} ya no es válida.")
            vistos.add(id_catalogo)
            resultado.append(id_catalogo)
        return resultado

    def _preparar_bibliografias(self, valores, id_formacion, id_solicitud_apoyo, id_estatus_apoyo):
        resultado = []
        vistos = set()
        for item in lista(valores, "Bibliografía"):
            if not isinstance(item, dict):
                raise FormacionComplementariaError(400, "Una bibliografía no tiene el formato esperado.")
            id_solicitud = entero_requerido(item.get("idSolicitudOrigen"), "asignatura origen", minimo=1)
            id_estatus = entero_requerido(item.get("idEstatusOrigen"), "estatus origen", minimo=1)
            id_bibliografia = entero_requerido(item.get("idBibliografiaOrigen"), "bibliografía origen", minimo=1)
            if id_solicitud != id_solicitud_apoyo or id_estatus != id_estatus_apoyo:
                raise FormacionComplementariaError(
                    400,
                    "Solo se puede seleccionar bibliografía de la versión vigente y concluida de la asignatura de apoyo elegida.",
                )
            clave = (id_solicitud, id_estatus, id_bibliografia)
            if clave in vistos:
                continue
            vistos.add(clave)
            bibliografia = self.db.obtener_bibliografia_exacta(*clave)
            if not bibliografia and id_formacion is not None:
                bibliografia = self.db.obtener_bibliografia_guardada(id_formacion, *clave)
            if not bibliografia:
                raise FormacionComplementariaError(
                    409,
                    "Una bibliografía seleccionada ya no está disponible. Actualiza la pantalla.",
                )
            resultado.append(dict(bibliografia))
        return resultado

    def _validar_completada(self, datos, temas, bibliografias, estrategias, id_usuario):
        obligatorios = {
            "id_area_conocimiento": "área del conocimiento",
            "semestre": "semestre",
            "horas_pract_semana": "horas prácticas por semana",
        }
        for campo, etiqueta in obligatorios.items():
            if datos.get(campo) is None:
                raise FormacionComplementariaError(
                    400,
                    f"El campo {etiqueta} es obligatorio para completar.",
                )

        if datos["horas_pract_semana"] <= 0:
            raise FormacionComplementariaError(
                400,
                "Las horas prácticas por semana deben ser mayores a cero.",
            )

        if not datos.get("objetivo_general"):
            raise FormacionComplementariaError(
                400,
                "El objetivo general es obligatorio para completar.",
            )

        if not temas:
            raise FormacionComplementariaError(
                400,
                "Debe registrar al menos un tema para completar.",
            )

        for tema in temas:
            if (
                not tema["tema"]
                or tema["horas_tema"] is None
                or tema["horas_tema"] <= 0
            ):
                raise FormacionComplementariaError(
                    400,
                    "Todos los temas deben tener nombre y horas enteras mayores a cero.",
                )

        horas_temas = sum((tema["horas_tema"] for tema in temas), 0)
        horas_semestre = datos["horas_pract_semestre"] or 0

        if horas_temas != horas_semestre:
            restantes = horas_semestre - horas_temas
            detalle = (
                f"Faltan {restantes} horas por asignar."
                if restantes > 0
                else f"El temario excede el total por {abs(restantes)} horas."
            )
            raise FormacionComplementariaError(
                400,
                f"Debe utilizar todas las horas prácticas del semestre ({horas_semestre}) en el temario. {detalle}",
            )

        disponibles = self.db.bibliografias_origen(
            datos["id_solicitud_apoyo"],
            id_usuario,
            datos.get("id_formacion"),
        )
        if not disponibles:
            raise FormacionComplementariaError(
                400,
                "La asignatura de apoyo no cuenta con bibliografía disponible; "
                "la formación complementaria no puede marcarse como completada.",
            )

        if not bibliografias:
            raise FormacionComplementariaError(
                400,
                "Seleccione al menos una bibliografía de la asignatura de apoyo.",
            )

        if not estrategias:
            raise FormacionComplementariaError(
                400,
                "Seleccione al menos una estrategia didáctica sugerida.",
            )

        if not datos.get("justificacion_academica"):
            raise FormacionComplementariaError(
                400,
                "La justificación académica es obligatoria para completar.",
            )

    def guardar(self, payload, id_usuario, usuario, completar=False):
        validar_payload_base(payload)
        generales = payload["datosGenerales"]
        if not isinstance(generales, dict):
            raise FormacionComplementariaError(400, "Los datos generales no tienen el formato esperado.")

        id_formacion = entero_opcional(payload.get("idFormacion"), "folio", minimo=1)
        existente = None
        estatus_origen = None
        if id_formacion is not None:
            existente = self.db.obtener_cabecera(id_formacion, id_usuario, for_update=True)
            if not existente:
                raise FormacionComplementariaError(404, "No se encontró la formación complementaria solicitada.")
            estatus_origen = int(existente["id_estatus_fc"])
            if estatus_origen == self.ESTATUS_COMPLETADA:
                raise FormacionComplementariaError(
                    409,
                    "La formación complementaria está completada y ya no puede modificarse.",
                )

        id_solicitud_apoyo = entero_requerido(
            generales.get("idSolicitudApoyo"), "asignatura de apoyo", minimo=1
        )
        id_subprograma = entero_requerido(generales.get("idSubprograma"), "subprograma", minimo=1)
        id_area_conocimiento = entero_requerido(
            generales.get("idAreaConocimiento"), "área del conocimiento", minimo=1
        )
        id_modalidad = entero_requerido(generales.get("idModalidad"), "modalidad", minimo=1)

        apoyo = self.db.asignatura_apoyo_activa(id_solicitud_apoyo, id_usuario, for_update=True)
        if not apoyo:
            raise FormacionComplementariaError(
                409,
                "La asignatura de apoyo debe pertenecer a la misma división del usuario, estar concluida, ser obligatoria y tener una clave válida de cuatro dígitos.",
            )
        subprograma = self.db.subprograma(id_subprograma)
        area_conocimiento = self.db.area_conocimiento(id_area_conocimiento)
        modalidad = self.db.modalidad(id_modalidad)
        if not subprograma or not area_conocimiento or not modalidad:
            raise FormacionComplementariaError(
                400,
                "El subprograma, el área del conocimiento o la modalidad seleccionada ya no es válida.",
            )

        # Reglas institucionales de Formación complementaria:
        # Tipo = Práctico y carácter = Optativo. Se fijan en servidor para impedir
        # que un POST manipulado cambie los valores mostrados como solo lectura.
        id_tipo = self.TIPO_PRACTICO
        id_caracter = self.CARACTER_OPTATIVO

        semestre = entero_opcional(generales.get("semestre"), "semestre", minimo=1, maximo=10)
        h_pra = self._hora_entera_opcional(generales.get("horasPracticasSemana"), "horas prácticas por semana")
        h_pra_semestre = None if h_pra is None else h_pra * self.SEMANAS_SEMESTRE

        nombre = self._normalizar_nombre(modalidad["prefijo_nombre"], apoyo["asignatura"])
        clave = self._clave_formacion(subprograma["clave_subprograma"], apoyo["clave_asignatura"])

        temas = self._preparar_temas(payload["temas"])
        estrategias = self._preparar_ids_catalogo(
            payload["estrategias"],
            "estrategias didácticas",
            "CATALOGO.TC_ESTRATEGIAS_DIDACTICAS",
            "ID_ESTRATEGIA_DIDACT",
        )
        bibliografias = self._preparar_bibliografias(
            payload["bibliografias"],
            id_formacion,
            id_solicitud_apoyo,
            int(apoyo["id_estatus_solicitud"]),
        )

        estatus_destino = self.ESTATUS_COMPLETADA if completar else self.ESTATUS_BORRADOR
        datos = {
            "id_formacion": id_formacion,
            "id_estatus_fc": estatus_destino,
            "id_solicitud_apoyo": id_solicitud_apoyo,
            "id_estatus_apoyo": int(apoyo["id_estatus_solicitud"]),
            "nombre_asignatura_apoyo": str(apoyo["asignatura"]),
            "clave_asignatura_apoyo": str(apoyo["clave_asignatura"]).strip(),
            "id_subprograma": id_subprograma,
            "id_area_conocimiento": id_area_conocimiento,
            "id_modalidad_fc": id_modalidad,
            "id_tipo_modalidad": id_tipo,
            "id_caracter_asig": id_caracter,
            "nombre_asignatura": nombre,
            "clave_asignatura": clave,
            "semestre": semestre,
            "horas_pract_semana": h_pra,
            "horas_pract_semestre": h_pra_semestre,
            "objetivo_general": texto(generales.get("objetivoGeneral"), max_length=4000),
            "justificacion_academica": texto(generales.get("justificacionAcademica"), max_length=self.MAX_JUSTIFICACION),
            "id_usuario": int(id_usuario),
            "usuario": usuario,
            "fecha_completada": None,
        }
        datos["id_formacion"] = id_formacion

        if completar:
            datos["id_formacion"] = id_formacion
            self._validar_completada(datos, temas, bibliografias, estrategias, id_usuario)
            datos["fecha_completada"] = "__SYSDATE__"

        # El repositorio usa un bind para fecha_completada. Para completada obtenemos SYSDATE
        # con una expresión controlada reemplazando el marcador por una fecha consultada por Oracle.
        if datos["fecha_completada"] == "__SYSDATE__":
            # Django/oracledb acepta datetime; se usa la hora del servidor de aplicación únicamente
            # para el bind. FECHA_MODIFICACION y BFECHA continúan usando SYSDATE Oracle.
            from django.utils import timezone
            datos["fecha_completada"] = timezone.now()

        try:
            if existente is None:
                id_formacion = self.db.siguiente_id()
                datos["id_formacion"] = id_formacion
                self.db.insertar_principal(datos)
                accion = "Creada y completada" if completar else "Creada"
                origen_historia = None
            else:
                datos["id_formacion"] = id_formacion
                self.db.actualizar_principal(datos)
                accion = "Completada" if completar else "Modificada"
                origen_historia = estatus_origen

            self.db.reemplazar_hijas(
                id_formacion,
                temas,
                bibliografias,
                estrategias,
                usuario,
            )
            self.db.registrar_historia(
                id_formacion,
                origen_historia,
                estatus_destino,
                accion,
                texto(payload.get("comentario"), max_length=1000),
                usuario,
            )
        except IntegrityError as exc:
            mensaje = str(exc).upper()
            if "FC_APOYO_UK" in mensaje:
                detalle = "La asignatura de apoyo ya fue utilizada en otra formación complementaria."
            elif "FC_NOMBRE_UK" in mensaje:
                detalle = "Ya existe una formación complementaria con el mismo nombre."
            elif "FC_CLAVE_UK" in mensaje:
                detalle = "Ya existe una formación complementaria con la misma clave."
            else:
                detalle = "No fue posible guardar porque existe información duplicada."
            raise FormacionComplementariaError(409, detalle) from exc

        return {
            "idFormacion": id_formacion,
            "estatus": estatus_destino,
            "nombre": nombre,
            "clave": clave,
            "mensaje": (
                "La formación complementaria se completó correctamente."
                if completar
                else "El borrador se guardó correctamente."
            ),
        }
