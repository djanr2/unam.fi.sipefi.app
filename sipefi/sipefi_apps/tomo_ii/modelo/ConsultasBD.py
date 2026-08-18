# -*- coding: utf-8 -*-
import secrets
import logging

logger = logging.getLogger(__name__)

from django.conf import settings
from django.contrib.auth.hashers import check_password, identify_hasher, make_password

from sipefi_apps.principal.modelo.ConexionBD import ConexionBD as conBD

class ConsultasBD():
        """
            Clase que nos apoya con la interaccion entre el servidor y la base de datos.
        """
        
        def __init__(self):
            """
                Funcion que ayuda a inicializar parametros y valores necesarios para las consultas SQL.
            """
            self.rol = ""
            self.idUniverso = ""
            
        def subConsultaRechazo(self):
            """
                Funcion que nos ayuda a crear una subconsulta sql para obtener las solicitudes que han sido rechazadas.
                
                :return: Regresa un String con la subconsulta sql.
            """
            sql = """
                    select a.id_solicitud, 'Rechazada' estatus, a.busuario, a.bfecha
                    from SIPEFI.TD_HISTORIA_SOLICITUD a 
                    where a.bfecha = (
                            select max(b.bfecha) from SIPEFI.TD_HISTORIA_SOLICITUD b
                            where 
                                a.ID_SOLICITUD = b.ID_SOLICITUD
                            group by b.ID_SOLICITUD
                    ) and (a.id_estatus_origen - a.id_estatus_destino) > 0
                    and a.id_estatus_destino not in (3)
            """
            return sql
            
        def buscaSolicitudesUsuario(self, usuario, rol):
            """
            Busca las solicitudes visibles para el usuario y perfil activo.

            """
            cursor = conBD().cursorBD()
            subQueryR = self.subConsultaRechazo()
            id_usuario = self.getIdUsuario(usuario)
            idsV = self.buscaRolXNombre("Validador")
            rol = int(rol)
            estatus = 2 if rol in idsV else 1

            sql_extra = ""
            params = {"estatus": estatus}

            if rol in idsV:  # Validadores
                sql_extra = """
                    AND a.id_solicitud NOT IN (
                        SELECT DISTINCT id_solicitud
                          FROM TD_SOLICITUD_TOMO_II
                         WHERE (
                                ID_USUARIO_CREACION = :id_usuario
                                OR ID_USUARIO_MOD = :id_usuario
                               )
                           AND historica = 1
                    )
                """
                params["id_usuario"] = id_usuario

                if rol != 17:  # Validador administrador ve todas las divisiones
                    sql_extra += """
                        AND EXISTS (
                            SELECT 1
                              FROM CATALOGO.TC_MAPEO_PERFIL mp
                             WHERE mp.id_perfil_origen = :rol
                               AND mp.id_perfil_destino = a.id_perfil
                               AND mp.activo = 0
                        )
                    """
                    params["rol"] = rol
            elif rol != 16:  # Operadores, excepto operador administrador
                sql_extra = """
                    AND (
                        a.ID_USUARIO_CREACION = :id_usuario
                        OR a.ID_USUARIO_MOD = :id_usuario
                    )
                """
                params["id_usuario"] = id_usuario

            sql_cons = f"""
                SELECT
                    'SIPEFI-'||a.id_solicitud,
                    a.asignatura,
                    CASE
                        WHEN c.estatus IS NOT NULL THEN c.estatus
                        ELSE b.desc_estatus
                    END,
                    ucrea.USUARIO_SISTEMA AS usuario_creacion,
                    umod.USUARIO_SISTEMA AS usuario_modificacion,
                    TO_CHAR(a.FECHA_MODIFICACION,'dd/mm/yyyy') fecha_mod,
                    '',
                    a.id_solicitud||'#@@#'||a.id_estatus_solicitud||'#@@#'||a.asignatura||'#@@#'||
                    umod.USUARIO_SISTEMA||'#@@#'||a.historica||'#@@#'||a.id_perfil||'#@@#'||ucrea.id_perfil
                  FROM TD_SOLICITUD_TOMO_II a
                  INNER JOIN CATALOGO.TC_ESTATUS_SOLICITUD b
                    ON a.id_estatus_solicitud = b.id_estatus_solicitud
                  LEFT JOIN ({subQueryR}) c
                    ON a.id_solicitud = c.id_solicitud
                  LEFT JOIN PARAMETRO.TP_USUARIO ucrea
                    ON a.ID_USUARIO_CREACION = ucrea.ID_USUARIO
                  LEFT JOIN PARAMETRO.TP_USUARIO umod
                    ON a.ID_USUARIO_MOD = umod.ID_USUARIO
                 WHERE a.historica = 0
                   AND a.id_estatus_solicitud = :estatus
                   {sql_extra}
                 ORDER BY a.id_solicitud DESC
            """
            try:
                data = cursor.execute(sql_cons, params)
                res = [app for app in data]
                res2 = self.buscaSolicitudesAvanzadas(id_usuario, estatus)
                res3 = self.buscaSolicitudesRecientes(id_usuario, estatus, subQueryR)
                respTotal = {
                    'TSU': res,
                    'estatusTSU': 200 if len(res) >= 1 else 204,
                    'TSA': res2,
                    'estatusTSA': 200 if len(res2) >= 1 else 204,
                    'TSR': res3,
                    'estatusTSR': 200 if len(res3) >= 1 else 204,
                    'catalogos': self.dameCatalogosIni(),
                    "infoAsigLic": self.buscaAsignaturasXLicenciatura(),
                }
            finally:
                cursor.close()
            return respTotal

        def buscaAsignaturasXLicenciatura(self):
            """
                Funcion que busca todas las asignaturas por licenciatura.
                
                :return: Regresa el objeto con la informacion de las asignaturas por licenciatura.
            """
            cursor = conBD().cursorBD()
            try:
                query = """
                    SELECT DISTINCT
                        s.id_solicitud AS num_solicitud,
                        s.id_estatus_solicitud AS id_estatus,
                        es.desc_estatus AS estatus_solicitud,
                        lic.id_licenciatura AS id_licenciatura,
                        lic.licenciatura AS nombre_licenciatura,
                        s.asignatura AS nombre_asignatura,
                        TO_CHAR(s.fecha_modificacion, 'DD/MM/YYYY') AS fecha_modificacion,
                        s.id_solicitud || '#@@#' || lic.id_licenciatura AS info_util
                    FROM SIPEFI.TD_SOLICITUD_TOMO_II s
                    JOIN SIPEFI.TD_REL_LIC_ASIGNATURA rla
                       ON rla.id_solicitud         = s.id_solicitud
                      AND rla.id_estatus_solicitud = s.id_estatus_solicitud
                    JOIN CATALOGO.TC_LICENCIATURA lic
                       ON lic.id_licenciatura = rla.id_licenciatura
                    JOIN CATALOGO.TC_ESTATUS_SOLICITUD es
                       ON es.id_estatus_solicitud = s.id_estatus_solicitud
                    WHERE s.historica = 0
                        and s.id_estatus_solicitud != 0
                    ORDER BY
                        lic.licenciatura,
                        s.id_solicitud
                """
                cursor.execute(query)
                res = cursor.fetchall()
            finally:
                cursor.close()
            return res
            
            
        def buscaSolicitudesAvanzadas(self, id_usuario, estatus):
            """
            Busca solicitudes en las que ha participado el usuario logueado.
            """
            cursor = conBD().cursorBD()
            try:
                extra_cond = """
                    a.ID_USUARIO_MOD = :id_usuario
                    AND a.ID_USUARIO_MOD != a.ID_USUARIO_CREACION
                """
                if int(estatus) == 1:  # Operativo
                    extra_cond = """
                        (
                            a.ID_USUARIO_MOD = :id_usuario
                            OR a.ID_USUARIO_CREACION = :id_usuario
                        )
                    """

                sql = f"""
                    SELECT
                        'SIPEFI-'||g.id_solicitud,
                        g.asignatura,
                        g.desc_estatus,
                        g.usuario_creacion,
                        g.usuario_modificacion,
                        TO_CHAR(g.fecha_mod,'dd/mm/yy'),
                        '<select class="accionSolicitud" id="numS'||g.id_solicitud||'"></select>',
                        (
                            SELECT LISTAGG(
                                       g.id_solicitud||'-'||a.id_estatus_solicitud||'||'||b.desc_estatus,
                                       '#@@#'
                                   ) WITHIN GROUP (ORDER BY a.id_estatus_solicitud) AS estatus
                              FROM TD_SOLICITUD_TOMO_II a
                              INNER JOIN CATALOGO.TC_ESTATUS_SOLICITUD b
                                ON a.id_estatus_solicitud = b.id_estatus_solicitud
                             WHERE a.id_solicitud = g.id_solicitud
                             GROUP BY a.id_solicitud
                        ) estatus
                      FROM (
                            SELECT DISTINCT
                                a.id_solicitud,
                                a.asignatura,
                                e.desc_estatus,
                                e.id_estatus_solicitud,
                                ucrea.USUARIO_SISTEMA AS usuario_creacion,
                                umod.USUARIO_SISTEMA AS usuario_modificacion,
                                a.FECHA_MODIFICACION AS fecha_mod
                              FROM TD_SOLICITUD_TOMO_II a
                              INNER JOIN (
                                    SELECT c.id_solicitud,
                                           MAX(c.id_estatus_solicitud) id_estatus
                                      FROM TD_SOLICITUD_TOMO_II c
                                     WHERE c.historica = 0
                                     GROUP BY c.id_solicitud
                              ) b
                                ON b.id_solicitud = a.id_solicitud
                              INNER JOIN CATALOGO.TC_ESTATUS_SOLICITUD e
                                ON b.id_estatus = e.id_estatus_solicitud
                              LEFT JOIN PARAMETRO.TP_USUARIO ucrea
                                ON a.ID_USUARIO_CREACION = ucrea.ID_USUARIO
                              LEFT JOIN PARAMETRO.TP_USUARIO umod
                                ON a.ID_USUARIO_MOD = umod.ID_USUARIO
                             WHERE a.historica = 0
                               AND {extra_cond}
                      ) g
                     WHERE g.id_estatus_solicitud NOT IN (:estatus, 0)
                     ORDER BY g.id_solicitud DESC
                """
                data = cursor.execute(sql, {
                    "id_usuario": id_usuario,
                    "estatus": int(estatus),
                })
                res = [app for app in data]
            finally:
                cursor.close()
            return res

        def buscaSolicitudesRecientes(self, id_usuario, estatus, subQueryR):
            """
            Busca solicitudes activas aprobadas (estatus 3) y procesadas por
            usuarios diferentes al usuario logueado.
            """
            cursor = conBD().cursorBD()
            try:
                sql = f"""
                    SELECT
                        'SIPEFI-'||a.id_solicitud,
                        a.asignatura,
                        CASE
                            WHEN c.estatus IS NOT NULL THEN c.estatus
                            ELSE b.desc_estatus
                        END,
                        ucrea.USUARIO_SISTEMA AS usuario_creacion,
                        umod.USUARIO_SISTEMA AS usuario_modificacion,
                        TO_CHAR(a.FECHA_MODIFICACION,'dd/mm/yyyy') fecha_mod,
                        '',
                        a.id_solicitud||'#@@#'||a.id_estatus_solicitud||'#@@#'||a.asignatura||'#@@#'||
                        umod.USUARIO_SISTEMA||'#@@#'||a.historica
                      FROM TD_SOLICITUD_TOMO_II a
                      INNER JOIN CATALOGO.TC_ESTATUS_SOLICITUD b
                        ON a.id_estatus_solicitud = b.id_estatus_solicitud
                      LEFT JOIN ({subQueryR}) c
                        ON a.id_solicitud = c.id_solicitud
                      LEFT JOIN PARAMETRO.TP_USUARIO ucrea
                        ON a.ID_USUARIO_CREACION = ucrea.ID_USUARIO
                      LEFT JOIN PARAMETRO.TP_USUARIO umod
                        ON a.ID_USUARIO_MOD = umod.ID_USUARIO
                     WHERE a.historica = 0
                       AND a.id_estatus_solicitud = 3
                       AND a.id_solicitud NOT IN (
                            SELECT DISTINCT id_solicitud
                              FROM TD_SOLICITUD_TOMO_II
                             WHERE (
                                    ID_USUARIO_MOD = :id_usuario
                                   )
                       )
                     ORDER BY a.id_solicitud DESC
                """
                data = cursor.execute(sql, {
                    "id_usuario": id_usuario,
                })
                res = [app for app in data]
            finally:
                cursor.close()
            return res

        def dameCatalogosIni(self):
            """
                Funcion principal que obtiene los catalogos iniciales del sistema SIPEFI - TOMO II.
                :return: Regresa objeto de tipo JSON con todos los catalogos iniciales.
            """
            catAreaCon = self.catalogoAreaConocimiento()
            catCarAsig = self.catalogoCaracterAsig()
            catEstDid = self.catalogoEstrategiaDidactica()
            catTipoBib = self.catalogoTipoBibliografia()
            catFormEval = self.catalogoFormasEvaluacion()
            catLic = self.catalogoLicenciaturas()
            catModalidad = self.catalogoModalidad()
            catTipoMod = self.catalogoTipoModalidad()
            catRelMod = self.catalogoRelacionModalidad()
            catAsig = self.catalogoAsignaturas()
            catValPract = self.catalogoValorPractico()
            res =   {'catAreaCon': catAreaCon, 'catCarAsig': catCarAsig,
                     'catEstDid': catEstDid, 'catTipoBib': catTipoBib,
                     'catFormEval': catFormEval, 'catLic': catLic,
                     'catModalidad': catModalidad, 'catTipoMod': catTipoMod,
                     'catRelMod': catRelMod, 'catAsig': catAsig, 'catValPract': catValPract,
                     'estatusACon': 200 if len(catAreaCon) >= 1 else 204,
                     'estatusCarAsig': 200 if len(catCarAsig) >= 1 else 204,
                     'estatusEstDid': 200 if len(catEstDid) >= 1 else 204,
                     'estatusTBib': 200 if len(catTipoBib) >= 1 else 204,
                     'estatusFEval': 200 if len(catFormEval) >= 1 else 204,
                     'estatusLic': 200 if len(catLic) >= 1 else 204,
                     'estatusMod': 200 if len(catModalidad) >= 1 else 204,
                     'estatusTMod': 200 if len(catTipoMod) >= 1 else 204,
                     'estatusRelMod': 200 if len(catRelMod) >= 1 else 204,
                     'estatusAsig': 200 if len(catAsig) >= 1 else 204,
                     'estatusVPract': 200 if len(catValPract) >= 1 else 204
                    }
            return res
        
        def catalogoAreaConocimiento(self):
            """
                Funcion que obtiene el catalogo de las areas de conocimiento.
                
                :return: Regresa objeto con el catalogo de los posibles valores para el area de conocmiento.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select id_area_conocimiento, area_conocimiento 
                    from catalogo.tc_area_conocimiento
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def catalogoAsignaturas(self):
            """
                Funcion que obtiene el catalogo de las asignaturas.
                
                :return: Regresa objeto con el catalogo de los posibles valores para las asignaturas.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select distinct id_asignatura, asignatura 
                    from sipefi.td_asignatura
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def catalogoValorPractico(self):
            """
                Funcion que obtiene el catalogo del valor practico.
                
                :return: Regresa objeto con el catalogo de los posibles valores para los valores practicos.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select id_valor_practico, valor_practico 
                    from catalogo.tc_valor_practico 
                    where id_valor_practico != 0
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def catalogoRelacionModalidad(self):
            """
                Funcion que obtiene el catalogo de la relacion entre la modalidad y el tipo de modalidad.
                
                :return: Regresa objeto con el catalogo de los valores de la relacion entre la modalidad y el tipo de modalidad.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select id_modalidad, id_tipo_modalidad 
                    from catalogo.tc_relacion_modalidad
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def catalogoTipoModalidad(self):
            """
                Funcion que obtiene el catalogo de los tipos de modalidades.
                
                :return: Regresa objeto con el catalogo de los posibles valores para los tipos de modalidad.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select id_tipo_modalidad, tipo_modalidad 
                    from catalogo.tc_tipo_modalidad
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def catalogoModalidad(self):
            """
                Funcion que obtiene el catalogo de las modalidades.
                
                :return: Regresa objeto con el catalogo de los posibles valores para las modalidades.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select id_modalidad, modalidad 
                    from catalogo.tc_modalidad
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def catalogoLicenciaturas(self):
            """
                Funcion que obtiene el catalogo de las licenciaturas de la FI.
                
                :return: Regresa objeto con el catalogo de los posibles valores para las licenciaturas.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select id_licenciatura, licenciatura 
                    from catalogo.tc_licenciatura
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def catalogoFormasEvaluacion(self):
            """
                Funcion que obtiene el catalogo de las formas de evaluacion.
                
                :return: Regresa objeto con el catalogo de los posibles valores para las formas de evaluacion.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select id_forma_eval, forma_evaluacion, tipo_evaluacion
                    from catalogo.tc_formas_evaluacion
                    where id_forma_eval != 0
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def catalogoTipoBibliografia(self):
            """
                Funcion que obtiene el catalogo de los tipos de bibliografias.
                
                :return: Regresa objeto con el catalogo de los posibles valores para los tipos de bibliografias.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select id_tipo_bibliografia, tipo_bibliografia 
                    from catalogo.tc_tipo_bibliografia
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def catalogoEstrategiaDidactica(self):
            """
                Funcion que obtiene el catalogo de las estrategias didacticas.
                
                :return: Regresa objeto con el catalogo de los posibles valores para las estrategias didacticas.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select id_estrategia_didact, estrategia_didactica 
                    from catalogo.tc_estrategias_didacticas
                    where id_estrategia_didact != 0
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def catalogoCaracterAsig(self):
            """
                Funcion que obtiene el catalogo del caracter de la asignatura.
                
                :return: Regresa objeto con el catalogo de los posibles valores para el caracter de la asignatura.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select id_caracter_asig, caracter_asignatura 
                    from catalogo.tc_caracter_asignatura
                    order by 1
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def actualizaEstatusToken(self, token):
            """
                Funcion que actualiza el estatus del token que se esta usando para la sesion del usuario y asi pueda continuar trabajando.
                
                :param token: Numero de token necesario para ingresar a la sesion de la aplicacion SIPEFI.
            """
            self.insertar("""
                UPDATE PARAMETRO.TP_ACCESOS
                   SET ESTATUS_ACCESO = 'E', FECHA_ACCESO = SYSDATE
                 WHERE TOKEN = :token
            """, {"token": token})
        
        def validaTokenAcceso(self, token):
            """
                Funcion que valida el token de acceso del usuario al sistema que desea ingresar.
                
                :param token: Numero de token que se desea validar para el acceso al sistema.
                
                :return: Regresa objeto con el estatus del acceso.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    SELECT a.token, b.usuario_sistema, b.id_perfil, a.id_usuario
                      FROM PARAMETRO.TP_ACCESOS a
                      INNER JOIN PARAMETRO.TP_USUARIO b
                        ON a.id_usuario = b.id_usuario
                     WHERE a.ESTATUS_ACCESO = 'E'
                       AND a.token = :token
                       AND ((SYSDATE - a.FECHA_ACCESO) * 24 * 60 * 60)
                           <= (SELECT valor
                                 FROM PARAMETRO.TP_PARAMETRO
                                WHERE parametro = 'DURACION_TOKEN')
                """, {"token": token})
                resp = [app for app in data]
                url = self.getUrlBadAccess()
                resp = {'acceso': resp,
                        'estatus': 200 if len(resp) >= 1 else 204,
                        'badAccess': url[0][0],
                        }
            finally:
                cursor.close()
            return resp
        
        def mapeoRolUsuario(self, id_perfil):
            """
                Funcion que ayuda a obtener todos los perfiles validos que tiene el usuario logueado, dado el
                caso que pueda fungir con mas de un perfil en el sistema logueado.
                
                :param id_perfil: Rol del usuario logueado.
                
                :return: Regresa objeto con el o los roles que puede tener el usuario en el sistema logueado.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    SELECT c.id_perfil, c.nombre_perfil
                      FROM CATALOGO.TC_PERFIL a
                      INNER JOIN CATALOGO.TC_MAPEO_PERFIL b
                        ON a.id_perfil = b.id_perfil_origen
                      INNER JOIN CATALOGO.TC_PERFIL c
                        ON b.id_perfil_destino = c.id_perfil
                     WHERE a.id_perfil = :id_perfil
                       AND a.activo = 0
                       AND c.activo = 0
                       AND b.activo = 0
                     ORDER BY 1
                """, {"id_perfil": int(id_perfil)})
                resp = [{"id": app[0], "rol": app[1]} for app in data]
                resp = {"resp": resp,
                        "estatus": 200 if len(resp) >= 1 else 204
                        }
            finally:
                cursor.close()
            return resp
    
        def getUrlBadAccess(self):
            """
                Funcion que obtiene la url de error dado el caso en el que no se tenga acceso al sistema.
                
                :return: Regresa string con la url del login de SIPEFI.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select valor from PARAMETRO.TP_PARAMETRO 
                    where parametro = 'url_sipefi_login'
                """)
                resp = [app for app in data]
            finally:
                cursor.close()
            return resp
        
        def getIdUsuario(self, usuario):
            """
            Función que obtiene el ID del perfil del usuario logueado.
        
            :param usuario: nombre de usuario del sistema
            :return: id_perfil del usuario o None si no se encuentra
            """
            cursor = conBD().cursorBD()
            try:
                cursor.execute("""
                    SELECT ID_USUARIO 
                    FROM PARAMETRO.TP_USUARIO 
                    WHERE USUARIO_SISTEMA = :usuario
                """, {'usuario': usuario})
                
                row = cursor.fetchone()
                return row[0] if row else None
            finally:
                cursor.close()
    
        def quemaTokenAcceso(self, token):
            """
                Funcion que ayuda a dejar inhabilitado el token de acceso del usuario, una vez que se ha usado.
                
                :param token: Parametro que contiene el token de acceso al sistema del usuario.
            """
            cursor = conBD().cursorBD()
            try:
                cursor.execute("""
                    UPDATE PARAMETRO.TP_ACCESOS
                       SET ESTATUS_ACCESO = 'A'
                     WHERE ESTATUS_ACCESO = 'E'
                       AND TOKEN = :token
                """, {"token": token})
            finally:
                cursor.close()
                
        def validar_credenciales(self, usuario_sistema, clave_acceso):
            """
            Valida las credenciales del usuario y genera un token de acceso.

            Compatibilidad de contraseñas:
            - Si CLAVE_ACCESO ya contiene un hash reconocido por Django, se valida
              con check_password().
            - Si todavía contiene la contraseña histórica en texto plano, se valida
              por igualdad.
            - Si SIPEFI_MIGRAR_PASSWORD_HASH está habilitado, después de un acceso
              correcto se migra automáticamente esa contraseña a un hash de Django.

            De esta forma los usuarios existentes no tienen que cambiar su
            contraseña y la migración puede habilitarse de manera progresiva.
            """
            cursor = conBD().cursorBD()
            try:
                cursor.execute("""
                    SELECT ID_USUARIO,
                           USUARIO_SISTEMA,
                           NOMBRE_COMPLETO,
                           ID_PERFIL,
                           CLAVE_ACCESO
                      FROM PARAMETRO.TP_USUARIO
                     WHERE USUARIO_SISTEMA = :usuario
                       AND ACTIVO = 0
                """, {
                    "usuario": usuario_sistema
                })
                row = cursor.fetchone()

                if not row:
                    return None

                id_usuario = row[0]
                clave_guardada = "" if row[4] is None else str(row[4])
                clave_recibida = "" if clave_acceso is None else str(clave_acceso)

                try:
                    identify_hasher(clave_guardada)
                    es_hash_django = True
                except ValueError:
                    es_hash_django = False

                if es_hash_django:
                    credenciales_validas = check_password(
                        clave_recibida,
                        clave_guardada
                    )
                else:
                    credenciales_validas = secrets.compare_digest(
                        clave_guardada.encode("utf-8"),
                        clave_recibida.encode("utf-8")
                    )

                if not credenciales_validas:
                    return None

                # Migración transparente: el primer login correcto de una cuenta
                # histórica reemplaza el texto plano por un hash seguro.
                if not es_hash_django and settings.SIPEFI_MIGRAR_PASSWORD_HASH:
                    cursor.execute("""
                        UPDATE PARAMETRO.TP_USUARIO
                           SET CLAVE_ACCESO = :clave_hash,
                               BFECHA = SYSDATE
                         WHERE ID_USUARIO = :id_usuario
                           AND CLAVE_ACCESO = :clave_actual
                    """, {
                        "clave_hash": make_password(clave_recibida),
                        "id_usuario": id_usuario,
                        "clave_actual": clave_guardada
                    })

                token = secrets.token_hex(32)  # Token seguro de 64 caracteres

                cursor.execute("""
                    INSERT INTO PARAMETRO.TP_ACCESOS (
                        ID_USUARIO, ESTATUS_ACCESO, MODULO, TOKEN
                    ) VALUES (
                        :id_usuario, 'E', 'Tomo II', :token
                    )
                """, {
                    "id_usuario": id_usuario,
                    "token": token
                })

                return {
                    "token": token,
                    "usuario": {
                        "id": row[0],
                        "usuario_sistema": row[1],
                        "nombre": row[2],
                        "id_perfil": row[3]
                    }
                }
            finally:
                cursor.close()

        def cierraSesionUsuario(self, token, id_usuario, opcion):
            """
                Funcion que ayuda a cerrar definitivamente la sesion del usuario.
                
                :param token: Parametro que contiene el token de acceso al sistema del usuario.
                :param usuario: Parametro que contiene el nombre del usuario logueado al sistema.
                :param opcion: Parametro que indica la opcion con la que se desea trabajar.
            """
            cursor = conBD().cursorBD()
            try:
                if int(opcion) == 1:
                    cursor.execute("""
                        UPDATE PARAMETRO.TP_ACCESOS
                           SET ESTATUS_ACCESO = 'I'
                         WHERE TOKEN = :token
                    """, {"token": token})
                else:
                    cursor.execute("""
                        UPDATE PARAMETRO.TP_ACCESOS
                           SET ESTATUS_ACCESO = 'I'
                         WHERE ID_USUARIO = :id_usuario
                           AND TOKEN <> :token
                    """, {"id_usuario": int(id_usuario), "token": token})
            finally:
                cursor.close()
            
        def validaSesionUsuario(self, token, opcion):
            """
                Funcion que ayuda a validar si la sesion del usuario aun se encuentra activa
                
                :param token: Token del usuario autenticado.
                :param opcion: Parametro que contiene la opcion con la que se desea trabajar.
            """
            cursor = conBD().cursorBD()
            try:
                cursor.execute("""
                    SELECT ESTATUS_ACCESO 
                    FROM PARAMETRO.TP_ACCESOS 
                    WHERE TOKEN = :token
                """, {'token': token})
        
                row = cursor.fetchone()
                resp = ""
        
                if int(opcion) == 1:
                    resp = "OK" if row and row[0] != 'I' else "NOK"
                else:
                    resp = row[0] if row else "NOK"
        
            except Exception:
                logger.exception("Error al validar la sesión del usuario.")
                resp = "NOK"
            finally:
                cursor.close()
            return resp
            
        def validaEstatus(self, idEstatus):
            """
                Funcion que ayuda a obtener el nombre del identificador del estatus de la solicitud.
                
                :param idEstatus: Identificador del estatus de la solicitud.
                
                :return: Regresa el nombre del identificador del estatus de la solicitud.
            """
            nomEstatus={
                0: 'Sol. Cancelada',
                1:'Elaboraci&oacute;n',
                2:'Revisi&oacute;n',
                3:'Concluida'
            }
            return nomEstatus.get(idEstatus,"NOK")
        
        def getNombrePerfil(self, id_perfil):
            """Obtiene el nombre del perfil activo por su identificador."""
            cursor = conBD().cursorBD()
            try:
                cursor.execute("""
                    SELECT nombre_perfil
                      FROM CATALOGO.TC_PERFIL
                     WHERE id_perfil = :id_perfil
                       AND activo = 0
                """, {"id_perfil": int(id_perfil)})
                row = cursor.fetchone()
                return row[0] if row else ""
            finally:
                cursor.close()

        def buscaRolXNombre(self, nombreRol):
            """
                Funcion que busca roles por filtro de nombre de rol.
                
                :param nombreRol: Parametro que contiene un fragmento de palabra del nombre de rol a buscar.
                
                :return: Regresa objeto con los roles encontrados con el filtro propuesto.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    SELECT id_perfil
                      FROM CATALOGO.TC_PERFIL
                     WHERE nombre_perfil LIKE :nombre_rol
                       AND activo = 0
                     ORDER BY 1
                """, {"nombre_rol": f"%{nombreRol}%"})
                resp = []
                for app in data:
                    resp.append(app[0])
            finally:
                cursor.close()
            return resp
        
        def insertaQuery(self, sql):
            """
                Funcion generica que ayuda a insertar en la base de datos de SIPEFI 
                alguna sentencia SQL pasada a esta funcion.
                
                :param sql: String con la sentencia SQL que se desea insertar en base de datos.
            """
            cursor = conBD().cursorBD()
            try:
                cursor.execute(sql)
            finally:
                cursor.close()
        
        def insertaQueryMasivo(self, query, obj):
            """
                Funcion que ayuda a insertar una sentencia sql de manera masiva.
                
                :param query: Parametro que contiene la sentencia sql a insertar de manera masiva.
                :param obj: Parametro que contiene los valores a insertar en la sentencia sql.
                
                :return: Regresa un booleano indicando si se inserto correctamente la sentencia sql.
            """
            resp = True
            try: 
                cursor = conBD().cursorBD()
                cursor.executemany(query,obj)
            except ValueError:
                resp = False
            finally:
                cursor.close()
            return resp
        
        def selectQuery(self, sql):
            """
                Funcion que ayuda a consultar una sentencia SQL en la base de datos de SIPEFI.
                
                :param sql: Parametro que contiene la sentencia SQL que se desea consultar en BD.
                
                :return: Regresa objeto con la informacion solicitada. 
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute(sql)
                res = [app for app in data]
            finally:
                cursor.close()
            return list(res)
        
        def insertaComentCLOB(self, sql, comment):
            """
                Funcion que ayuda insertar los comentarios de las solicitudes en la base de datos, los cuales son tratados como tipo
                de dato CLOB.
                
                :param sql: Sentencia SQL que se desea insertar en BD.
                :param comment: Parametro que contiene el comentario de la solicitud.
            """
            cursor = conBD().cursorBD()
            try:
                cursor.execute(sql, [comment])
            finally:
                cursor.close()
                
        def conexion(self):
            """
            Retorna la conexión activa a la base de datos configurada en Django.
            """
            return conBD().conexion()
        
        def insertar(self, sql, params=None):
            """
            Ejecuta sentencias INSERT/UPDATE/DELETE con o sin parámetros.
            """
            cursor = conBD().cursorBD()
            try:
                cursor.execute(sql, params or [])
            except Exception:
                logger.exception("Error al ejecutar una operación DML en SIPEFI.")
                raise
            finally:
                cursor.close()
                
        def consulta(self, sql, params=None):
            """
            Ejecuta un SELECT y retorna todos los resultados.
            """
            cursor = conBD().cursorBD()
            try:
                cursor.execute(sql, params or [])
                return cursor.fetchall()
            finally:
                cursor.close()