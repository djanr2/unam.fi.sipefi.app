# -*- coding: utf-8 -*-
from collections import OrderedDict

from sipefi_apps.principal.modelo.ConexionBD import ConexionBD


def _valor_json(valor):
    if hasattr(valor, "read"):
        return valor.read()
    return valor


def _filas_diccionario(cursor):
    columnas = [col[0].lower() for col in cursor.description]
    return [OrderedDict((columnas[i], _valor_json(valor)) for i, valor in enumerate(fila)) for fila in cursor.fetchall()]


class ConsultasBD:

    ESTATUS_CONCLUIDA = 3
    CARACTER_OBLIGATORIA = 1

    def _cursor(self):
        return ConexionBD().cursorBD()

    def catalogos(self):
        cursor = self._cursor()
        try:
            respuesta = {}
            consultas = {
                "subprogramas": """
                    SELECT id_subprograma AS id, clave_subprograma AS clave,
                           subprograma AS nombre
                      FROM CATALOGO.TC_SUBPROGRAMA_FC
                     WHERE activo = 0
                     ORDER BY clave_subprograma
                """,
                "modalidades": """
                    SELECT id_modalidad_fc AS id, modalidad AS nombre,
                           prefijo_nombre AS prefijo
                      FROM CATALOGO.TC_MODALIDAD_FC
                     WHERE activo = 0
                     ORDER BY id_modalidad_fc
                """,
                "areas_conocimiento": """
                    SELECT id_area_conocimiento AS id,
                           area_conocimiento AS nombre
                      FROM CATALOGO.TC_AREA_CONOCIMIENTO
                     WHERE id_area_conocimiento <> 0
                     ORDER BY id_area_conocimiento
                """,
                "estrategias": """
                    SELECT id_estrategia_didact AS id, estrategia_didactica AS nombre
                      FROM CATALOGO.TC_ESTRATEGIAS_DIDACTICAS
                     WHERE id_estrategia_didact <> 0
                     ORDER BY estrategia_didactica
                """,
            }
            for nombre, sql in consultas.items():
                cursor.execute(sql)
                respuesta[nombre] = _filas_diccionario(cursor)
            return respuesta
        finally:
            cursor.close()

    def asignaturas_disponibles(self, id_usuario, id_formacion=None):
        cursor = self._cursor()
        try:
            params = {
                "id_usuario": int(id_usuario),
                "estatus_concluida": self.ESTATUS_CONCLUIDA,
                "caracter_obligatoria": self.CARACTER_OBLIGATORIA,
                "patron_clave": r"^[0-9]{4}$",
            }
            inclusion_actual = ""
            if id_formacion is not None:
                inclusion_actual = """
                    OR EXISTS (
                        SELECT 1
                          FROM SIPEFI.TD_FORMACION_COMPLEMENTARIA fc_actual
                         WHERE fc_actual.id_formacion = :id_formacion
                           AND fc_actual.id_solicitud_apoyo = s.id_solicitud
                    )
                """
                params["id_formacion"] = int(id_formacion)

            sql = f"""
                SELECT s.id_solicitud,
                       s.id_estatus_solicitud,
                       s.asignatura,
                       TRIM(s.clave_asignatura) AS clave_asignatura,
                       es.desc_estatus
                  FROM SIPEFI.TD_SOLICITUD_TOMO_II s
                  JOIN CATALOGO.TC_ESTATUS_SOLICITUD es
                    ON es.id_estatus_solicitud = s.id_estatus_solicitud
                  JOIN PARAMETRO.TP_USUARIO u_creador
                    ON u_creador.id_usuario = s.id_usuario_creacion
                  JOIN PARAMETRO.TP_USUARIO u_actual
                    ON u_actual.id_usuario = :id_usuario
                 WHERE s.historica = 0
                   AND u_creador.id_division = u_actual.id_division
                   AND s.id_estatus_solicitud = :estatus_concluida
                   AND REGEXP_LIKE(
                       TRIM(s.clave_asignatura),
                       :patron_clave
                   )
                   AND EXISTS (
                        SELECT 1
                          FROM SIPEFI.TD_REL_LIC_ASIGNATURA rel
                         WHERE rel.id_solicitud = s.id_solicitud
                           AND rel.id_estatus_solicitud = s.id_estatus_solicitud
                           AND rel.id_caracter_asig = :caracter_obligatoria
                   )
                   AND (
                        NOT EXISTS (
                            SELECT 1
                              FROM SIPEFI.TD_FORMACION_COMPLEMENTARIA fc
                             WHERE fc.id_solicitud_apoyo = s.id_solicitud
                        )
                        {inclusion_actual}
                   )
                 ORDER BY UPPER(s.asignatura), s.id_solicitud
            """
            cursor.execute(sql, params)
            resultado = _filas_diccionario(cursor)
            if id_formacion is not None:
                ids = {int(item["id_solicitud"]) for item in resultado}
                cursor.execute(
                    """
                    SELECT id_solicitud_apoyo AS id_solicitud,
                           id_estatus_apoyo AS id_estatus_solicitud,
                           nombre_asignatura_apoyo AS asignatura,
                           clave_asignatura_apoyo AS clave_asignatura,
                           'Copia conservada' AS desc_estatus
                      FROM SIPEFI.TD_FORMACION_COMPLEMENTARIA
                     WHERE id_formacion = :id_formacion
                       AND id_estatus_fc = 2
                    """,
                    {"id_formacion": int(id_formacion)},
                )
                copia = _filas_diccionario(cursor)
                if copia and int(copia[0]["id_solicitud"]) not in ids:
                    resultado.append(copia[0])
            resultado.sort(key=lambda item: (str(item.get("asignatura", "")).upper(), int(item["id_solicitud"])))
            return resultado
        finally:
            cursor.close()

    def listar_propias(self, id_usuario):
        cursor = self._cursor()
        try:
            cursor.execute(
                """
                SELECT fc.id_formacion,
                       fc.nombre_asignatura_apoyo AS asignatura_apoyo,
                       fc.nombre_asignatura,
                       fc.clave_asignatura,
                       sub.subprograma,
                       mod.modalidad,
                       fc.semestre,
                       est.desc_estatus AS estatus,
                       fc.id_estatus_fc,
                       TO_CHAR(fc.fecha_modificacion, 'DD/MM/YYYY HH24:MI') AS fecha_modificacion
                  FROM SIPEFI.TD_FORMACION_COMPLEMENTARIA fc
                  JOIN CATALOGO.TC_SUBPROGRAMA_FC sub
                    ON sub.id_subprograma = fc.id_subprograma
                  JOIN CATALOGO.TC_MODALIDAD_FC mod
                    ON mod.id_modalidad_fc = fc.id_modalidad_fc
                  JOIN CATALOGO.TC_ESTATUS_FC est
                    ON est.id_estatus_fc = fc.id_estatus_fc
                 WHERE fc.id_usuario_creacion = :id_usuario
                 ORDER BY fc.fecha_modificacion DESC, fc.id_formacion DESC
                """,
                {"id_usuario": int(id_usuario)},
            )
            return _filas_diccionario(cursor)
        finally:
            cursor.close()

    def obtener_cabecera(self, id_formacion, id_usuario, for_update=False):
        cursor = self._cursor()
        try:
            bloqueo = " FOR UPDATE" if for_update else ""
            cursor.execute(
                f"""
                SELECT fc.*
                  FROM SIPEFI.TD_FORMACION_COMPLEMENTARIA fc
                 WHERE fc.id_formacion = :id_formacion
                   AND fc.id_usuario_creacion = :id_usuario
                {bloqueo}
                """,
                {"id_formacion": int(id_formacion), "id_usuario": int(id_usuario)},
            )
            filas = _filas_diccionario(cursor)
            return filas[0] if filas else None
        finally:
            cursor.close()

    def obtener_detalle(self, id_formacion, id_usuario):
        cabecera = self.obtener_cabecera(id_formacion, id_usuario)
        if not cabecera:
            return None

        cursor = self._cursor()
        try:
            cursor.execute(
                """
                SELECT num_tema, tema, horas_tema
                  FROM SIPEFI.TD_TEMA_FORMACION_COMP
                 WHERE id_formacion = :id_formacion
                 ORDER BY num_tema
                """,
                {"id_formacion": int(id_formacion)},
            )
            temas = _filas_diccionario(cursor)

            cursor.execute(
                """
                SELECT id_bibliografia_fc, id_solicitud_origen, id_estatus_origen,
                       id_bibliografia_origen, es_complementaria,
                       id_tipo_bibliografia, autor, publicacion, titulo,
                       campo_1, campo_2, campo_3, campo_4, temas_recomienda
                  FROM SIPEFI.TD_BIBLIO_FORMACION_COMP
                 WHERE id_formacion = :id_formacion
                 ORDER BY id_bibliografia_fc
                """,
                {"id_formacion": int(id_formacion)},
            )
            bibliografias = _filas_diccionario(cursor)

            cursor.execute(
                """
                SELECT id_estrategia_didact AS id
                  FROM SIPEFI.TD_REL_FC_ESTRATEGIA
                 WHERE id_formacion = :id_formacion
                 ORDER BY id_estrategia_didact
                """,
                {"id_formacion": int(id_formacion)},
            )
            estrategias = [fila[0] for fila in cursor.fetchall()]

            cabecera["temas"] = temas
            cabecera["bibliografias_seleccionadas"] = bibliografias
            cabecera["estrategias"] = estrategias
            return cabecera
        finally:
            cursor.close()

    def asignatura_apoyo_activa(self, id_solicitud, id_usuario, for_update=False):
        cursor = self._cursor()
        try:
            bloqueo = " FOR UPDATE OF s.id_solicitud" if for_update else ""
            cursor.execute(
                f"""
                SELECT s.id_solicitud, s.id_estatus_solicitud, s.asignatura,
                       s.clave_asignatura
                  FROM SIPEFI.TD_SOLICITUD_TOMO_II s
                  JOIN PARAMETRO.TP_USUARIO u_creador
                    ON u_creador.id_usuario = s.id_usuario_creacion
                  JOIN PARAMETRO.TP_USUARIO u_actual
                    ON u_actual.id_usuario = :id_usuario
                 WHERE s.id_solicitud = :id_solicitud
                   AND s.historica = 0
                   AND u_creador.id_division = u_actual.id_division
                   AND s.id_estatus_solicitud = :estatus_concluida
                   AND REGEXP_LIKE(
                       TRIM(s.clave_asignatura),
                       :patron_clave
                   )
                   AND EXISTS (
                        SELECT 1
                          FROM SIPEFI.TD_REL_LIC_ASIGNATURA rel
                         WHERE rel.id_solicitud = s.id_solicitud
                           AND rel.id_estatus_solicitud = s.id_estatus_solicitud
                           AND rel.id_caracter_asig = :caracter_obligatoria
                   )
                {bloqueo}
                """,
                {
                    "id_solicitud": int(id_solicitud),
                    "id_usuario": int(id_usuario),
                    "estatus_concluida": self.ESTATUS_CONCLUIDA,
                    "caracter_obligatoria": self.CARACTER_OBLIGATORIA,
                    "patron_clave": r"^[0-9]{4}$",
                },
            )
            filas = _filas_diccionario(cursor)
            return filas[0] if len(filas) == 1 else None
        finally:
            cursor.close()

    def subprograma(self, id_subprograma):
        cursor = self._cursor()
        try:
            cursor.execute(
                """
                SELECT id_subprograma, clave_subprograma, subprograma
                  FROM CATALOGO.TC_SUBPROGRAMA_FC
                 WHERE id_subprograma = :id_subprograma
                   AND activo = 0
                """,
                {"id_subprograma": int(id_subprograma)},
            )
            filas = _filas_diccionario(cursor)
            return filas[0] if filas else None
        finally:
            cursor.close()

    def modalidad(self, id_modalidad):
        cursor = self._cursor()
        try:
            cursor.execute(
                """
                SELECT id_modalidad_fc, modalidad, prefijo_nombre
                  FROM CATALOGO.TC_MODALIDAD_FC
                 WHERE id_modalidad_fc = :id_modalidad
                   AND activo = 0
                """,
                {"id_modalidad": int(id_modalidad)},
            )
            filas = _filas_diccionario(cursor)
            return filas[0] if filas else None
        finally:
            cursor.close()

    def area_conocimiento(self, id_area_conocimiento):
        cursor = self._cursor()
        try:
            cursor.execute(
                """
                SELECT id_area_conocimiento, area_conocimiento
                  FROM CATALOGO.TC_AREA_CONOCIMIENTO
                 WHERE id_area_conocimiento = :id_area_conocimiento
                   AND id_area_conocimiento <> 0
                """,
                {"id_area_conocimiento": int(id_area_conocimiento)},
            )
            filas = _filas_diccionario(cursor)
            return filas[0] if filas else None
        finally:
            cursor.close()

    def existe_catalogo(self, tabla, columna, valor):
        permitidos = {
            ("CATALOGO.TC_ESTRATEGIAS_DIDACTICAS", "ID_ESTRATEGIA_DIDACT"),
        }
        if (tabla, columna) not in permitidos:
            return False
        cursor = self._cursor()
        try:
            cursor.execute(
                f"SELECT 1 FROM {tabla} WHERE {columna} = :valor AND {columna} <> 0",
                {"valor": int(valor)},
            )
            return cursor.fetchone() is not None
        finally:
            cursor.close()

    def bibliografias_origen(self, id_solicitud, id_usuario, id_formacion=None):
        apoyo = self.asignatura_apoyo_activa(id_solicitud, id_usuario)
        cursor = self._cursor()
        try:
            actuales = []
            if apoyo:
                cursor.execute(
                    """
                    SELECT b.id_solicitud AS id_solicitud_origen,
                           b.id_estatus_solicitud AS id_estatus_origen,
                           b.id_bibliografia AS id_bibliografia_origen,
                           b.es_complementaria,
                           b.id_tipo_bibliografia,
                           tb.tipo_bibliografia,
                           b.autor, b.publicacion, b.titulo,
                           b.campo_1, b.campo_2, b.campo_3, b.campo_4,
                           b.temas_recomienda
                      FROM SIPEFI.TD_BIBLIOGRAFIA b
                      LEFT JOIN CATALOGO.TC_TIPO_BIBLIOGRAFIA tb
                        ON tb.id_tipo_bibliografia = b.id_tipo_bibliografia
                     WHERE b.id_solicitud = :id_solicitud
                       AND b.id_estatus_solicitud = :id_estatus
                     ORDER BY b.es_complementaria, b.id_bibliografia
                    """,
                    {
                        "id_solicitud": int(id_solicitud),
                        "id_estatus": int(apoyo["id_estatus_solicitud"]),
                    },
                )
                actuales = _filas_diccionario(cursor)

            seleccionadas = []
            if id_formacion is not None:
                cursor.execute(
                    """
                    SELECT bfc.id_solicitud_origen, bfc.id_estatus_origen,
                           bfc.id_bibliografia_origen, bfc.es_complementaria,
                           bfc.id_tipo_bibliografia, tb.tipo_bibliografia,
                           bfc.autor, bfc.publicacion, bfc.titulo,
                           bfc.campo_1, bfc.campo_2, bfc.campo_3, bfc.campo_4,
                           bfc.temas_recomienda
                      FROM SIPEFI.TD_BIBLIO_FORMACION_COMP bfc
                      LEFT JOIN CATALOGO.TC_TIPO_BIBLIOGRAFIA tb
                        ON tb.id_tipo_bibliografia = bfc.id_tipo_bibliografia
                     WHERE bfc.id_formacion = :id_formacion
                     ORDER BY bfc.id_bibliografia_fc
                    """,
                    {"id_formacion": int(id_formacion)},
                )
                seleccionadas = _filas_diccionario(cursor)

            seleccion_por_id = {
                int(item["id_bibliografia_origen"]): item for item in seleccionadas
            }
            resultado = []
            ids_incluidos = set()
            for item in actuales:
                bibliografia_id = int(item["id_bibliografia_origen"])
                if bibliografia_id in seleccion_por_id:
                    copia = seleccion_por_id[bibliografia_id]
                    copia["tipo_bibliografia"] = item.get("tipo_bibliografia")
                    copia["seleccionada"] = True
                    copia["disponible_origen"] = True
                    resultado.append(copia)
                else:
                    item["seleccionada"] = False
                    item["disponible_origen"] = True
                    resultado.append(item)
                ids_incluidos.add(bibliografia_id)

            for item in seleccionadas:
                bibliografia_id = int(item["id_bibliografia_origen"])
                if bibliografia_id not in ids_incluidos:
                    item["seleccionada"] = True
                    item["disponible_origen"] = False
                    resultado.append(item)
            return resultado
        finally:
            cursor.close()

    def obtener_bibliografia_exacta(self, id_solicitud, id_estatus, id_bibliografia):
        cursor = self._cursor()
        try:
            cursor.execute(
                """
                SELECT id_solicitud AS id_solicitud_origen,
                       id_estatus_solicitud AS id_estatus_origen,
                       id_bibliografia AS id_bibliografia_origen,
                       es_complementaria, id_tipo_bibliografia,
                       autor, publicacion, titulo,
                       campo_1, campo_2, campo_3, campo_4, temas_recomienda
                  FROM SIPEFI.TD_BIBLIOGRAFIA
                 WHERE id_solicitud = :id_solicitud
                   AND id_estatus_solicitud = :id_estatus
                   AND id_bibliografia = :id_bibliografia
                """,
                {
                    "id_solicitud": int(id_solicitud),
                    "id_estatus": int(id_estatus),
                    "id_bibliografia": int(id_bibliografia),
                },
            )
            filas = _filas_diccionario(cursor)
            return filas[0] if filas else None
        finally:
            cursor.close()

    def obtener_bibliografia_guardada(self, id_formacion, id_solicitud, id_estatus, id_bibliografia):
        cursor = self._cursor()
        try:
            cursor.execute(
                """
                SELECT id_solicitud_origen, id_estatus_origen,
                       id_bibliografia_origen, es_complementaria,
                       id_tipo_bibliografia, autor, publicacion, titulo,
                       campo_1, campo_2, campo_3, campo_4, temas_recomienda
                  FROM SIPEFI.TD_BIBLIO_FORMACION_COMP
                 WHERE id_formacion = :id_formacion
                   AND id_solicitud_origen = :id_solicitud
                   AND id_estatus_origen = :id_estatus
                   AND id_bibliografia_origen = :id_bibliografia
                """,
                {
                    "id_formacion": int(id_formacion),
                    "id_solicitud": int(id_solicitud),
                    "id_estatus": int(id_estatus),
                    "id_bibliografia": int(id_bibliografia),
                },
            )
            filas = _filas_diccionario(cursor)
            return filas[0] if filas else None
        finally:
            cursor.close()

    def siguiente_id(self):
        cursor = self._cursor()
        try:
            cursor.execute("SELECT SIPEFI.SEQ_FORMACION_COMPLEMENTARIA.NEXTVAL FROM DUAL")
            return int(cursor.fetchone()[0])
        finally:
            cursor.close()

    def insertar_principal(self, datos):
        cursor = self._cursor()
        try:
            cursor.execute(
                """
                INSERT INTO SIPEFI.TD_FORMACION_COMPLEMENTARIA (
                    id_formacion, id_estatus_fc, id_solicitud_apoyo, id_estatus_apoyo,
                    nombre_asignatura_apoyo, clave_asignatura_apoyo,
                    id_subprograma, id_area_conocimiento, id_modalidad_fc, id_tipo_modalidad, id_caracter_asig,
                    nombre_asignatura, clave_asignatura, semestre,
                    horas_pract_semana, horas_pract_semestre,
                    objetivo_general, justificacion_academica,
                    id_usuario_creacion, id_usuario_modificacion,
                    fecha_creacion, fecha_modificacion, fecha_completada,
                    busuario, bfecha
                ) VALUES (
                    :id_formacion, :id_estatus_fc, :id_solicitud_apoyo, :id_estatus_apoyo,
                    :nombre_asignatura_apoyo, :clave_asignatura_apoyo,
                    :id_subprograma, :id_area_conocimiento, :id_modalidad_fc, :id_tipo_modalidad, :id_caracter_asig,
                    :nombre_asignatura, :clave_asignatura, :semestre,
                    :horas_pract_semana, :horas_pract_semestre,
                    :objetivo_general, :justificacion_academica,
                    :id_usuario, :id_usuario,
                    SYSDATE, SYSDATE, :fecha_completada,
                    :usuario, SYSDATE
                )
                """,
                datos,
            )
        finally:
            cursor.close()

    def actualizar_principal(self, datos):
        cursor = self._cursor()
        try:
            cursor.execute(
                """
                UPDATE SIPEFI.TD_FORMACION_COMPLEMENTARIA
                   SET id_estatus_fc = :id_estatus_fc,
                       id_solicitud_apoyo = :id_solicitud_apoyo,
                       id_estatus_apoyo = :id_estatus_apoyo,
                       nombre_asignatura_apoyo = :nombre_asignatura_apoyo,
                       clave_asignatura_apoyo = :clave_asignatura_apoyo,
                       id_subprograma = :id_subprograma,
                       id_area_conocimiento = :id_area_conocimiento,
                       id_modalidad_fc = :id_modalidad_fc,
                       id_tipo_modalidad = :id_tipo_modalidad,
                       id_caracter_asig = :id_caracter_asig,
                       nombre_asignatura = :nombre_asignatura,
                       clave_asignatura = :clave_asignatura,
                       semestre = :semestre,
                       horas_pract_semana = :horas_pract_semana,
                       horas_pract_semestre = :horas_pract_semestre,
                       objetivo_general = :objetivo_general,
                       justificacion_academica = :justificacion_academica,
                       id_usuario_modificacion = :id_usuario,
                       fecha_modificacion = SYSDATE,
                       fecha_completada = :fecha_completada,
                       busuario = :usuario,
                       bfecha = SYSDATE
                 WHERE id_formacion = :id_formacion
                """,
                datos,
            )
        finally:
            cursor.close()

    def reemplazar_hijas(self, id_formacion, temas, bibliografias, estrategias, usuario):
        cursor = self._cursor()
        try:
            params = {"id_formacion": int(id_formacion)}
            cursor.execute("DELETE FROM SIPEFI.TD_REL_FC_ESTRATEGIA WHERE id_formacion = :id_formacion", params)
            cursor.execute("DELETE FROM SIPEFI.TD_BIBLIO_FORMACION_COMP WHERE id_formacion = :id_formacion", params)
            cursor.execute("DELETE FROM SIPEFI.TD_TEMA_FORMACION_COMP WHERE id_formacion = :id_formacion", params)

            for tema in temas:
                cursor.execute(
                    """
                    INSERT INTO SIPEFI.TD_TEMA_FORMACION_COMP (
                        id_formacion, num_tema, tema, horas_tema, busuario, bfecha
                    ) VALUES (
                        :id_formacion, :num_tema, :tema, :horas_tema, :usuario, SYSDATE
                    )
                    """,
                    {"id_formacion": id_formacion, "usuario": usuario, **tema},
                )

            for indice, bibliografia in enumerate(bibliografias, start=1):
                cursor.execute(
                    """
                    INSERT INTO SIPEFI.TD_BIBLIO_FORMACION_COMP (
                        id_formacion, id_bibliografia_fc,
                        id_solicitud_origen, id_estatus_origen, id_bibliografia_origen,
                        es_complementaria, id_tipo_bibliografia,
                        autor, publicacion, titulo, campo_1, campo_2, campo_3, campo_4,
                        temas_recomienda, busuario, bfecha
                    ) VALUES (
                        :id_formacion, :id_bibliografia_fc,
                        :id_solicitud_origen, :id_estatus_origen, :id_bibliografia_origen,
                        :es_complementaria, :id_tipo_bibliografia,
                        :autor, :publicacion, :titulo, :campo_1, :campo_2, :campo_3, :campo_4,
                        :temas_recomienda, :usuario, SYSDATE
                    )
                    """,
                    {
                        "id_formacion": id_formacion,
                        "id_bibliografia_fc": indice,
                        "usuario": usuario,
                        **bibliografia,
                    },
                )

            for id_estrategia in estrategias:
                cursor.execute(
                    """
                    INSERT INTO SIPEFI.TD_REL_FC_ESTRATEGIA (
                        id_formacion, id_estrategia_didact, busuario, bfecha
                    ) VALUES (:id_formacion, :id, :usuario, SYSDATE)
                    """,
                    {"id_formacion": id_formacion, "id": id_estrategia, "usuario": usuario},
                )

        finally:
            cursor.close()

    def registrar_historia(self, id_formacion, origen, destino, accion, comentario, usuario):
        cursor = self._cursor()
        try:
            cursor.execute(
                """
                INSERT INTO SIPEFI.TD_HISTORIA_FORMACION_COMP (
                    id_historia_fc, id_formacion, id_estatus_origen,
                    id_estatus_destino, accion, comentario, busuario, bfecha
                ) VALUES (
                    SIPEFI.SEQ_HISTORIA_FORMACION_COMP.NEXTVAL,
                    :id_formacion, :origen, :destino, :accion, :comentario,
                    :usuario, SYSDATE
                )
                """,
                {
                    "id_formacion": id_formacion,
                    "origen": origen,
                    "destino": destino,
                    "accion": accion,
                    "comentario": comentario,
                    "usuario": usuario,
                },
            )
        finally:
            cursor.close()
