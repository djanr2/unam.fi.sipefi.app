# -*- coding: utf-8 -*-

import secrets

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
                Funcion que busca todas las solicitudes pendientes de concluir por el usuario logueado.
                
                :param usuario: Usuario logueado.
                :param rol: Rol del usuario logueado.
                :param universo: Id del proyecto que se esta trabajando.
                
                :return: Objeto que contiene la informacion de las solicitudes procesadas por el usuario logueado.  
            """
            cursor = conBD().cursorBD()
            subQueryR = self.subConsultaRechazo()
            id_usuario = self.getIdUsuario(usuario)
            idsV = self.buscaRolXNombre("Validador")
            rol = int(rol)
            estatus = 2 if rol in idsV else 1
            sqlExtra = ""
            if rol in idsV:
                sqlExtra = """ 
                            a.id_solicitud not in 
                            (select distinct id_solicitud 
                                from TD_SOLICITUD_TOMO_II 
                                where ID_USUARIO_CREACION = '""" + str(id_usuario) + """' and historica = 1
                            )
                """
            else:
                sqlExtra = " a.ID_USUARIO_CREACION = '" + str(id_usuario) + "'"
     
            sqlCons = """
                        SELECT 'SIPEFI-'||a.id_solicitud, g.asignatura,
                        case when c.estatus is not null then c.estatus else b.desc_estatus end, 
                        a.ID_USUARIO_CREACION,
                        a.ID_USUARIO_MOD,
                        TO_CHAR(a.FECHA_MODIFICACION,'dd/mm/yyyy') fecha_mod,
                        '', a.id_solicitud||'#@@#'||a.id_estatus_solicitud||'#@@#'||g.asignatura||'#@@#'||
                        d.USUARIO_SISTEMA||'#@@#'||a.historica||'#@@#'||a.id_perfil
                        from TD_SOLICITUD_TOMO_II a inner join catalogo.TC_ESTATUS_SOLICITUD b 
                            on a.id_estatus_solicitud = b.id_estatus_solicitud
                        left join (""" + subQueryR + """) c on a.id_solicitud = c.id_solicitud
                        inner join PARAMETRO.TP_USUARIO d
                            on a.ID_USUARIO_MOD = d.ID_USUARIO
                        inner join (
                            select distinct f.id_solicitud, f.id_estatus_solicitud, f.id_asignatura from TD_REL_LIC_ASIGNATURA f
                        ) e
                            on a.id_solicitud = e.id_solicitud and a.id_estatus_solicitud = e.id_estatus_solicitud
                        inner join TD_ASIGNATURA g
                            on e.id_asignatura = g.id_asignatura
                        where a.historica = 0 and a.id_estatus_solicitud in (""" + str(estatus) + """) and """ + sqlExtra + """
                        order by a.id_solicitud desc
            """
            try:
                data = cursor.execute(sqlCons)
                res = [app for app in data]
                res2 = self.buscaSolicitudesAvanzadas(id_usuario, estatus)
                res3 = self.buscaSolicitudesRecientes(id_usuario, estatus, subQueryR)
                respTotal = {'TSU': res,
                             'estatusTSU': 200 if len(res) >= 1 else 204 ,
                             'TSA': res2,
                             'estatusTSA': 200 if len(res2) >= 1 else 204,
                             'TSR': res3,
                             'estatusTSR': 200 if len(res3) >= 1 else 204,
                             'catalogos': self.dameCatalogosIni()
                             }
            finally:
                cursor.close()
            return respTotal
        
        def buscaSolicitudesAvanzadas(self, id_usuario, estatus):
            """
                Funcion que busca todas las solicitudes en las que ha participado el usuario logueado.
                
                :param id_usuario: ID del usuario logueado.
                :param estatus: Estatus de solicitud que no debe ser considerado en la busqueda de solicitudes.
                
                :return: Regresa el objeto con la informacion de las solicitudes donde el usuario ha participado.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                            select 'SIPEFI-'||g.id_solicitud, g.asignatura, g.desc_estatus, g.usu_crea, g.usu_mod, TO_CHAR(fecha_mod,'dd/mm/yy'), '<select class="accionSolicitud" id="numS'||g.id_solicitud||'"></select>',
                                (select LISTAGG(g.id_solicitud||'-'||a.id_estatus_solicitud||'||'||b.desc_estatus, '#@@#') WITHIN GROUP (ORDER BY a.id_estatus_solicitud) AS estatus 
                                    from TD_SOLICITUD_TOMO_II a
                                    inner join CATALOGO.TC_ESTATUS_SOLICITUD b
                                    on a.id_estatus_solicitud = b.id_estatus_solicitud
                                    where a.id_solicitud = g.id_solicitud group by a.id_solicitud
                                ) estatus
                            from (
                                select distinct 
                                    a.id_solicitud, c.asignatura , e.desc_estatus, e.id_estatus_solicitud,
                                    a.ID_USUARIO_CREACION usu_crea,
                                    a.ID_USUARIO_MOD usu_mod,
                                    a.FECHA_MODIFICACION fecha_mod
                                from TD_SOLICITUD_TOMO_II a
                                inner join (
                                  select distinct f.id_solicitud, f.id_estatus_solicitud, f.id_asignatura from TD_REL_LIC_ASIGNATURA f
                                ) b
                                on a.id_solicitud = b.id_solicitud and a.id_estatus_solicitud = b.id_estatus_solicitud
                                inner join TD_ASIGNATURA c
                                on b.id_asignatura = c.id_asignatura
                                inner join (
                                    select c.id_solicitud, max(c.id_estatus_solicitud) id_estatus
                                    from TD_SOLICITUD_TOMO_II c 
                                    where c.historica = 0 group by c.id_solicitud
                                ) d
                                on d.id_solicitud = a.id_solicitud
                                inner join CATALOGO.TC_ESTATUS_SOLICITUD e
                                on d.id_estatus = e.id_estatus_solicitud
                                where a.ID_USUARIO_MOD = '""" + str(id_usuario) + """'
                            ) g where g.id_estatus_solicitud != '""" + str(estatus) + """' 
                            order by g.id_solicitud desc
                """)
                res = [app for app in data]
            finally:
                cursor.close()
            return res
        
        def buscaSolicitudesRecientes(self, id_usuario, estatus, subQueryR):
            """
                Funcion que busca todas las solicitudes que han sido procesadas por usuarios diferentes al usuario logueado.
                
                :param usuario: Usuario logueado.
                :param tablaSoli: Nombre de la tabla donde se buscaran las solicitudes en base de datos.
                :param subQueryR: Subquery que debe ser agregada al query de consulta.
                
                :return: Regresa el objeto con la informacion de las solicitudes que han sido procesadas por usuarios diferentes al usuario logueado.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    SELECT 'SIPEFI-'||a.id_solicitud, g.asignatura,
                        case when c.estatus is not null then c.estatus else b.desc_estatus end,
                        a.ID_USUARIO_CREACION,
                        a.ID_USUARIO_MOD,
                        TO_CHAR(a.FECHA_MODIFICACION,'dd/mm/yyyy') fecha_mod,
                        '', a.id_solicitud||'#@@#'||a.id_estatus_solicitud||'#@@#'||g.asignatura||'#@@#'||
                        d.USUARIO_SISTEMA||'#@@#'||a.historica
                    from TD_SOLICITUD_TOMO_II a inner join catalogo.TC_ESTATUS_SOLICITUD b 
                        on a.id_estatus_solicitud = b.id_estatus_solicitud
                    left join ("""+subQueryR+""") c on a.id_solicitud = c.id_solicitud
                    inner join PARAMETRO.TP_USUARIO d
                        on a.ID_USUARIO_MOD = d.ID_USUARIO
                    inner join (
                        select distinct f.id_solicitud, f.id_estatus_solicitud, f.id_asignatura from TD_REL_LIC_ASIGNATURA f
                    ) e
                    on a.id_solicitud = e.id_solicitud and a.id_estatus_solicitud = e.id_estatus_solicitud
                    inner join TD_ASIGNATURA g
                    on e.id_asignatura = g.id_asignatura
                    where a.historica = 0 and a.id_estatus_solicitud >= '""" + str(estatus) + """' and 
                    a.id_solicitud not in 
                                (select distinct id_solicitud 
                                    from TD_SOLICITUD_TOMO_II 
                                    where ID_USUARIO_MOD = '""" + str(id_usuario) + """'
                                )
                    order by a.id_solicitud desc
                """)
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
            res =   {'catAreaCon': catAreaCon, 'catCarAsig': catCarAsig,
                     'catEstDid': catEstDid, 'catTipoBib': catTipoBib,
                     'catFormEval': catFormEval, 'catLic': catLic,
                     'catModalidad': catModalidad, 'catTipoMod': catTipoMod,
                     'catRelMod': catRelMod, 'catAsig': catAsig,
                     'estatusACon': 200 if len(catAreaCon) >= 1 else 204,
                     'estatusCarAsig': 200 if len(catCarAsig) >= 1 else 204,
                     'estatusEstDid': 200 if len(catEstDid) >= 1 else 204,
                     'estatusTBib': 200 if len(catTipoBib) >= 1 else 204,
                     'estatusFEval': 200 if len(catFormEval) >= 1 else 204,
                     'estatusLic': 200 if len(catLic) >= 1 else 204,
                     'estatusMod': 200 if len(catModalidad) >= 1 else 204,
                     'estatusTMod': 200 if len(catTipoMod) >= 1 else 204,
                     'estatusRelMod': 200 if len(catRelMod) >= 1 else 204,
                     'estatusAsig': 200 if len(catAsig) >= 1 else 204
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
                    order by 2
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
                    select id_forma_eval, forma_evaluacion
                    from catalogo.tc_formas_evaluacion
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
            sql = """
                update PARAMETRO.TP_ACCESOS set estatus_acceso = 'E', fecha_acceso = sysdate 
                where token = '"""+str(token)+"""'
            """
            self.insertaQuery(sql)
        
        def validaTokenAcceso(self, token):
            """
                Funcion que valida el token de acceso del usuario al sistema que desea ingresar.
                
                :param token: Numero de token que se desea validar para el acceso al sistema.
                
                :return: Regresa objeto con el estatus del acceso.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                    select a.token, b.usuario_sistema, b.id_perfil, a.id_usuario
                    from parametro.TP_ACCESOS a
                    inner join parametro.TP_USUARIO b
                      on a.id_usuario = b.id_usuario
                    where a.ESTATUS_ACCESO = 'E' and a.token = '""" + str(token) + """' and 
                         ((sysdate - a.FECHA_ACCESO)*24*60*60) 
                          <= (select valor from parametro.tp_parametro b where b.parametro = 'DURACION_TOKEN')
                """)
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
                    select c.id_perfil, c.nombre_perfil
                    from catalogo.TC_PERFIL a
                    inner join catalogo.TC_MAPEO_PERFIL b 
                      on a.id_perfil = b.id_perfil_origen 
                    inner join catalogo.TC_PERFIL c
                      on b.id_perfil_destino = c.id_perfil
                    where a.id_perfil = '""" + str(id_perfil) + """' 
                    and a.activo = '0' and c.activo = '0' 
                    order by 1
                """)
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
                    SELECT ID_PERFIL 
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
                   update parametro.TP_ACCESOS set estatus_acceso = 'A'
                   where estatus_acceso = 'E' and token = '""" + str(token) + """'
                """)
            finally:
                cursor.close()
                
        def validar_credenciales(self, usuario_sistema, clave_acceso):
            """
            Valida las credenciales de un usuario y genera un token si son correctas.
        
            Parámetros:
            - usuario_sistema: nombre de usuario ingresado por el usuario
            - clave_acceso: contraseña ingresada por el usuario
    
            Retorna:
            - Un diccionario con el token y datos del usuario si son válidos.
            - None si las credenciales son incorrectas.
            """
            cursor = conBD().cursorBD()
            try:
                cursor.execute("""
                    SELECT ID_USUARIO, USUARIO_SISTEMA, NOMBRE_COMPLETO, ID_PERFIL
                    FROM PARAMETRO.TP_USUARIO
                    WHERE USUARIO_SISTEMA = :usuario 
                      AND CLAVE_ACCESO = :clave  
                      AND ACTIVO = 0
                """, {
                    'usuario': usuario_sistema,
                    'clave': clave_acceso
                })
                row = cursor.fetchone()
                if row:
                    id_usuario = row[0]
                    token = secrets.token_hex(32)  # Token seguro de 64 caracteres
    
                    # Insertar registro de acceso
                    cursor.execute("""
                        INSERT INTO PARAMETRO.TP_ACCESOS (
                            ID_USUARIO, ESTATUS_ACCESO, MODULO, TOKEN
                        ) VALUES (
                            :id_usuario, 'E', 'Tomo II', :token
                        )
                    """, {
                        'id_usuario': id_usuario,
                        'token': token
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
    
                else:
                    return None
            finally:
                cursor.close()
                
        def cierraSesionUsuario(self, token, id_usuario, opcion):
            """
                Funcion que ayuda a cerrar definitivamente la sesion del usuario.
                
                :param token: Parametro que contiene el token de acceso al sistema del usuario.
                :param usuario: Parametro que contiene el nombre del usuario logueado al sistema.
                :param opcion: Parametro que indica la opcion con la que se desea trabajar.
            """
            condicion = ""
            if int(opcion) == 1:
                condicion = " token = '" + token + "'"
            else:
                condicion = " id_usuario = '" + str(id_usuario) + "' and token != '" + str(token) + "'"
            cursor = conBD().cursorBD()
            try:
                cursor.execute("""
                   update parametro.TP_ACCESOS set estatus_acceso = 'I'
                   where """ + condicion + """
                """)
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
        
            except Exception as e:
                print(e)
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
        
        def buscaRolXNombre(self, nombreRol):
            """
                Funcion que busca roles por filtro de nombre de rol.
                
                :param nombreRol: Parametro que contiene un fragmento de palabra del nombre de rol a buscar.
                
                :return: Regresa objeto con los roles encontrados con el filtro propuesto.
            """
            cursor = conBD().cursorBD()
            try:
                data = cursor.execute("""
                            select id_perfil from catalogo.TC_PERFIL
                            where nombre_perfil like '%"""+nombreRol+"""%'
                            and activo = '0' order by 1
                        """)
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