# -*- coding: utf-8 -*-
from sipefi_apps.tomo_ii.modelo.ConsultasBD import ConsultasBD as CBD

from datetime import datetime

class Solicitud:
    """
    Clase que gestiona el flujo completo de una solicitud en el sistema SIPEFI,
    incluyendo creación, edición, aprobación, rechazo y trazabilidad de acciones.
    """

    def __init__(self):
        self.db = CBD()
        self.id_solicitud = None
        self.id_estatus = None
        self.nom_estatus = None
        self.usuario = None
        self.rol = None
        self.token = None

    def procesar(self, obj):
        """
        Procesa la acción solicitada sobre una solicitud: guardar, aprobar o rechazar.

        :param obj: Objeto JSON recibido desde el frontend.
        :return: Diccionario con resultado y metadatos.
        """
        accion = int(obj.get("accionSoli"))
        self.token = obj.get("metadatos", {}).get("token")
        self.rol = int(obj.get("metadatos", {}).get("rol", 0))
        if accion == 1: #Guardar o actualizar
            return self.guardar_o_actualizar(obj)
        elif accion == 2: #procesar solicitud
            return self.procesar_aprobacion(obj)
        elif accion == 3: #rechazar solicitud
            return self.rechazar_solicitud(obj)
        else:
            raise ValueError("Acción no reconocida")

    def guardar_o_actualizar(self, obj):
        """
        Inserta o actualiza una solicitud y todas sus tablas relacionadas.

        :param obj: Objeto de solicitud completo.
        :return: Diccionario con identificadores y nombre de estatus.
        """
        def limpiar_num(valor):
            return int(valor) if str(valor).isdigit() else None
    
        try:
            accion = "Guardado o Edición"
            datos = obj.get("datosGenerales", {})
            estrategias = obj.get("estrategiasEvaluacion", {})
            metadatos = obj.get("metadatos", {})

            nombre_usuario = metadatos.get("usuarioSoli")
            self.usuario = nombre_usuario
            id_usuario = self.db.getIdUsuario(nombre_usuario)
            num_solicitud_raw = metadatos.get("numSolicitud")
            id_estatus_raw = metadatos.get("idEstSoli")
            self.id_solicitud = int(num_solicitud_raw) if str(num_solicitud_raw).isnumeric() else 0
            self.id_estatus = int(id_estatus_raw) if str(id_estatus_raw).isnumeric() else 1
            self.nom_estatus = self.obtener_nombre_estatus(self.id_estatus)
            
            # Si la solicitud ya existe, conservar creador y fecha
            id_usuario_creacion, fecha_creacion = None, None
            asignatura = datos.get("nombreAsignatura", "")
            if self.id_solicitud > 0: #solicitud existente
                id_usuario_creacion, fecha_creacion, asignatura = self.obtener_datos_creacion()
            elif self.id_solicitud == 0: #solicitud nueva
                accion = "Creación"
                self.id_solicitud = self.db.consulta("SELECT NVL(MAX(id_solicitud), 0) + 1 FROM SIPEFI.TD_SOLICITUD_TOMO_II")[0][0]
                
                #Validamos que no exista la asignatura
                existeAsig = self.db.consulta("""
                    SELECT COUNT(*) AS total
                    FROM SIPEFI.TD_ASIGNATURA
                    WHERE UPPER(asignatura) = UPPER(:nombre_asignatura)
                """, {
                    "nombre_asignatura": asignatura
                })[0][0]
                
                if existeAsig > 0:
                    raise Exception((409, f"La asignatura <strong>'{asignatura}'</strong> ya existe"))
                else:
                    #Insertar asignatura en tabla de asignaturas
                    sql = """
                        INSERT INTO SIPEFI.TD_ASIGNATURA (
                            id_asignatura, asignatura, plan_estudios, busuario
                        ) VALUES (
                            :id_asignatura, :asignatura, '2025', :usuario 
                            
                        )
                    """
                    params = {
                        "id_asignatura": self.id_solicitud,
                        "asignatura": asignatura,
                        "usuario": self.usuario
                    }
                    self.db.insertar(sql, params)
            
            #Limpiamos solicitud primero
            self.limpiar_solicitud(self.id_solicitud, self.id_estatus)
            
            # Insertar encabezado
            sql = """
                INSERT INTO SIPEFI.TD_SOLICITUD_TOMO_II (
                    id_solicitud, id_estatus_solicitud, historica, asignatura, clave_asignatura, creditos, id_area_conocimiento,
                    id_modalidad, id_tipo_modalidad, id_caracter_asig, horas_teo_semana,
                    horas_pract_semana, horas_teo_semestre, horas_pract_semestre,
                    objetivo_general, actividades_practicas, formacion_integral,
                    perfil_profesiografico, id_perfil, fecha_creacion, fecha_modificacion,
                    id_usuario_creacion, id_usuario_mod
                ) VALUES (
                    :id_solicitud, :id_estatus_solicitud, 0, :asignatura, :clave_asignatura, :creditos, 
                    :id_area_conocimiento, :id_modalidad, :id_tipo_modalidad, :id_caracter_asig, :horas_teo_semana,
                    :horas_pract_semana, :horas_teo_semestre, :horas_pract_semestre,
                    :objetivo_general, :actividades_practicas, :formacion_integral,
                    :perfil_profesiografico, :id_perfil, :fecha_creacion, SYSDATE,
                    :id_usuario_creacion, :id_usuario_mod
                )
            """
            params = {
                "id_solicitud": self.id_solicitud,
                "id_estatus_solicitud": self.id_estatus,
                "asignatura": asignatura,
                "clave_asignatura": datos.get("claveAsignatura"),
                "creditos": limpiar_num(datos.get("creditos")),
                "id_area_conocimiento": limpiar_num(datos.get("areaConocimiento")),
                "id_modalidad": limpiar_num(datos.get("modalidad")),
                "id_tipo_modalidad": limpiar_num(datos.get("tipoModalidad")),
                "id_caracter_asig": limpiar_num(datos.get("caracterAsignatura")),
                "horas_teo_semana": limpiar_num(datos.get("hSemTeoria")),
                "horas_pract_semana": limpiar_num(datos.get("hSemPractica")),
                "horas_teo_semestre": limpiar_num(datos.get("hSemestreTeoria")),
                "horas_pract_semestre": limpiar_num(datos.get("hSemestrePractica")),
                "objetivo_general": datos.get("objAsig") or "",
                "actividades_practicas": obj.get("actPracticas") or "",
                "formacion_integral": estrategias.get("formacionIntegral") or "",
                "perfil_profesiografico": estrategias.get("perfilProfesiografico") or "",
                "id_perfil": limpiar_num(metadatos.get("rol")),
                "fecha_creacion": fecha_creacion or datetime.now(),
                "id_usuario_creacion": id_usuario_creacion or id_usuario,
                "id_usuario_mod": id_usuario
            }
            self.db.insertar(sql, params)

            # Insertar detalles
            self._insertar_valor_practico(datos.get("valorPractico", []))
            self._insertar_rel_licenciaturas(obj.get("relacionLicenciaturas", []))
            self._insertar_temario(obj.get("temario", []))
            self._insertar_contenido(obj.get("contenido", []))
            self._insertar_bibliografia(obj.get("bibliografia", []))
            self._insertar_estrategias(estrategias)

            # Guardar historial
            comentario = metadatos.get("comentarios")
            self._guardar_traza(comentario, self.id_estatus, self.id_estatus, accion)
            
            #Actualizamos token
            self._actualizar_token()
            return {"idS": self.id_solicitud, "idES": self.id_estatus, "nomES": self.nom_estatus}

        except Exception as e:
            print(e)
            raise

    def procesar_aprobacion(self, obj):
        """
        Procesa una solicitud al siguiente estatus (Estatus + 1).
        Guarda traza del cambio de estatus y actualiza token.

        :param obj: Objeto completo de solicitud.
        :return: Diccionario con estatus actualizado.
        """
        try:
            self.id_solicitud = int(obj.get("metadatos", {}).get("numSolicitud"))
            self.id_estatus   = int(obj.get("metadatos", {}).get("idEstSoli"))
            self.usuario      = obj.get("metadatos", {}).get("usuarioSoli")
            comentario        = obj.get("metadatos", {}).get("comentarios")
    
            if self.id_estatus >= 3:
                # Ya está concluida: no avanza
                return {"idS": self.id_solicitud, "idES": self.id_estatus, "nomES": self.obtener_nombre_estatus(self.id_estatus)}
    
            nuevo_estatus = self.id_estatus + 1
            id_usuario_mod = self.db.getIdUsuario(self.usuario)
    
            # Marcamos versión actual como histórica
            self.db.insertar("""
                UPDATE SIPEFI.TD_SOLICITUD_TOMO_II
                SET historica = 1, fecha_modificacion = SYSDATE, id_usuario_mod = :id_usuario_mod
                WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :id_estatus
            """, {"id_usuario_mod": id_usuario_mod, "id_solicitud": self.id_solicitud, "id_estatus": self.id_estatus})
    
            # Limpiamos cualquier residuo en el estatus destino e insertamos clon de la solicitud en el nuevo estatus
            self.limpiar_solicitud(self.id_solicitud, nuevo_estatus)
            self._clonar_version(self.id_solicitud, self.id_estatus, nuevo_estatus, self.usuario)
    
            # Guardamos Traza y actualizamos token
            accion = "Envío a validación" if nuevo_estatus == 2 else "Aprobado"
            self._guardar_traza(comentario, self.id_estatus, nuevo_estatus, accion)
            self._actualizar_token()
    
            return {"idS": self.id_solicitud, "idES": nuevo_estatus, "nomES": self.obtener_nombre_estatus(nuevo_estatus)}
        except Exception:
            raise

    def rechazar_solicitud(self, obj):
        """
        Marca la solicitud como rechazada, copia su traza y actualiza el token.

        :param obj: Objeto de solicitud.
        :return: Diccionario de confirmación.
        """
        try:
            self.id_solicitud = int(obj.get("metadatos", {}).get("numSolicitud"))
            self.id_estatus   = int(obj.get("metadatos", {}).get("idEstSoli"))
            self.usuario      = obj.get("metadatos", {}).get("usuarioSoli")
            comentario        = obj.get("metadatos", {}).get("comentarios")
            id_usuario_mod    = self.db.getIdUsuario(self.usuario)
    
            if self.id_estatus <= 1:
                # No hay versión anterior para reactivar
                self._guardar_traza(comentario, self.id_estatus, self.id_estatus, "Rechazada (sin versión anterior)")
                self._actualizar_token()
                return {"idS": self.id_solicitud, "idES": self.id_estatus, "nomES": "Elaboración"}
    
            estatus_anterior = self.id_estatus - 1
    
            # Borramos la versión actual completa
            self.limpiar_solicitud(self.id_solicitud, self.id_estatus)
    
            # Reactivamos la versión anterior
            self.db.insertar("""
                UPDATE SIPEFI.TD_SOLICITUD_TOMO_II
                SET historica = 0, fecha_modificacion = SYSDATE, id_usuario_mod = :id_usuario_mod
                WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :estatus_anterior
            """, {"id_usuario_mod": id_usuario_mod, "id_solicitud": self.id_solicitud, "estatus_anterior": estatus_anterior})
    
            # Guardamos traza y actualizamos token
            self._guardar_traza(comentario, self.id_estatus, estatus_anterior, "Rechazada")
            self._actualizar_token()
    
            return {"idS": self.id_solicitud, "idES": estatus_anterior, "nomES": self.obtener_nombre_estatus(estatus_anterior)}
        except Exception:
            raise
            
    def _clonar_version(self, id_soli, est_origen, est_destino, usuario_mod):
        """Clonamos la solicitud para guardar el nuevo estatus de la solicitud."""
        # Encabezado
        self.db.insertar("""
            INSERT INTO SIPEFI.TD_SOLICITUD_TOMO_II (
                id_solicitud, id_estatus_solicitud, historica, asignatura, clave_asignatura, creditos,
                id_area_conocimiento, id_modalidad, id_tipo_modalidad, id_caracter_asig,
                horas_teo_semana, horas_pract_semana, horas_teo_semestre, horas_pract_semestre,
                objetivo_general, actividades_practicas, formacion_integral, perfil_profesiografico, id_perfil,
                fecha_creacion, fecha_modificacion, id_usuario_creacion, id_usuario_mod
            )
            SELECT
                id_solicitud, :est_destino, 0, asignatura, clave_asignatura, creditos,
                id_area_conocimiento, id_modalidad, id_tipo_modalidad, id_caracter_asig,
                horas_teo_semana, horas_pract_semana, horas_teo_semestre, horas_pract_semestre,
                objetivo_general, actividades_practicas, formacion_integral, perfil_profesiografico, id_perfil,
                fecha_creacion, SYSDATE, id_usuario_creacion, :id_usuario_mod
            FROM SIPEFI.TD_SOLICITUD_TOMO_II
            WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :est_origen
        """, {
            "id_solicitud": id_soli, "est_origen": est_origen,
            "est_destino": est_destino, "id_usuario_mod": self.db.getIdUsuario(usuario_mod)
        })
    
        # Hijas
        self.db.insertar("""
            INSERT INTO SIPEFI.TD_REL_VAL_PRACTICO (id_solicitud, id_estatus_solicitud, id_valor_practico, busuario)
            SELECT id_solicitud, :est_destino, id_valor_practico, :busuario
            FROM SIPEFI.TD_REL_VAL_PRACTICO
            WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :est_origen
        """, {"id_solicitud": id_soli, "est_origen": est_origen, "est_destino": est_destino, "busuario": usuario_mod})
    
        self.db.insertar("""
            INSERT INTO SIPEFI.TD_REL_LIC_ASIGNATURA (id_solicitud, id_estatus_solicitud, id_licenciatura, seriacion_ant, seriacion_cons, semestre, busuario)
            SELECT id_solicitud, :est_destino, id_licenciatura, seriacion_ant, seriacion_cons, semestre, :busuario
            FROM SIPEFI.TD_REL_LIC_ASIGNATURA
            WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :est_origen
        """, {"id_solicitud": id_soli, "est_origen": est_origen, "est_destino": est_destino, "busuario": usuario_mod})
    
        self.db.insertar("""
            INSERT INTO SIPEFI.TD_TEMARIO_ASIGNATURA (id_solicitud, id_estatus_solicitud, num_tema, tema, objetivo, horas_tema, busuario)
            SELECT id_solicitud, :est_destino, num_tema, tema, objetivo, horas_tema, :busuario
            FROM SIPEFI.TD_TEMARIO_ASIGNATURA
            WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :est_origen
        """, {"id_solicitud": id_soli, "est_origen": est_origen, "est_destino": est_destino, "busuario": usuario_mod})
    
        self.db.insertar("""
            INSERT INTO SIPEFI.TD_CONTENIDO_TEMATICO (id_solicitud, id_estatus_solicitud, num_tema, num_contenido, contenido, busuario)
            SELECT id_solicitud, :est_destino, num_tema, num_contenido, contenido, :busuario
            FROM SIPEFI.TD_CONTENIDO_TEMATICO
            WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :est_origen
        """, {"id_solicitud": id_soli, "est_origen": est_origen, "est_destino": est_destino, "busuario": usuario_mod})
    
        self.db.insertar("""
            INSERT INTO SIPEFI.TD_BIBLIOGRAFIA (id_solicitud, id_estatus_solicitud, id_bibliografia, es_complementaria, id_tipo_bibliografia,
                                                autor, publicacion, titulo, campo_1, campo_2, campo_3, campo_4, temas_recomienda, busuario)
            SELECT id_solicitud, :est_destino, id_bibliografia, es_complementaria, id_tipo_bibliografia,
                   autor, publicacion, titulo, campo_1, campo_2, campo_3, campo_4, temas_recomienda, :busuario
            FROM SIPEFI.TD_BIBLIOGRAFIA
            WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :est_origen
        """, {"id_solicitud": id_soli, "est_origen": est_origen, "est_destino": est_destino, "busuario": usuario_mod})
    
        self.db.insertar("""
            INSERT INTO SIPEFI.TD_REL_ASIG_EVALUACION (id_solicitud, id_estatus_solicitud, id_forma_eval, busuario)
            SELECT id_solicitud, :est_destino, id_forma_eval, :busuario
            FROM SIPEFI.TD_REL_ASIG_EVALUACION
            WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :est_origen
        """, {"id_solicitud": id_soli, "est_origen": est_origen, "est_destino": est_destino, "busuario": usuario_mod})
    
        self.db.insertar("""
            INSERT INTO SIPEFI.TD_REL_ASIG_ESTRAT_DID (id_solicitud, id_estatus_solicitud, id_estrategia_didact, busuario)
            SELECT id_solicitud, :est_destino, id_estrategia_didact, :busuario
            FROM SIPEFI.TD_REL_ASIG_ESTRAT_DID
            WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :est_origen
        """, {"id_solicitud": id_soli, "est_origen": est_origen, "est_destino": est_destino, "busuario": usuario_mod})
    
    def obtener_datos_creacion(self):
        """
        Consulta la fecha y el ID del usuario que creó originalmente la solicitud.
    
        :param id_solicitud: ID de la solicitud
        :param id_estatus: ID del estatus de la solicitud
        :return: Tuple (id_usuario_creacion, fecha_creacion) o (None, None)
        """
        row = self.db.consulta("""
            SELECT id_usuario_creacion, fecha_creacion, asignatura
            FROM SIPEFI.TD_SOLICITUD_TOMO_II
            WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :id_estatus
        """, {
            "id_solicitud": self.id_solicitud,
            "id_estatus": self.id_estatus
        })
        
        return (row[0][0], row[0][1], row[0][2]) if row else (None, None, None)

    def limpiar_solicitud(self, id_soli, id_est):
        tablas = [
            "TD_REL_LIC_ASIGNATURA", "TD_CONTENIDO_TEMATICO", "TD_TEMARIO_ASIGNATURA",
            "TD_BIBLIOGRAFIA", "TD_REL_ASIG_EVALUACION", "TD_REL_ASIG_ESTRAT_DID",
            "TD_REL_VAL_PRACTICO", "TD_SOLICITUD_TOMO_II"
        ]
        for tabla in tablas:
            sql = f"""
                DELETE FROM SIPEFI.{tabla}
                WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :id_estatus
            """
            params = {
                "id_solicitud": id_soli,
                "id_estatus": id_est
            }
            self.db.insertar(sql, params)

    def _insertar_valor_practico(self, valores):
        """
        Inserta las relaciones de valor práctico asociadas a la solicitud.
    
        :param valores: Lista de IDs de valor práctico desde datosGenerales["valorPractico"]
        """
        for val in valores:
            self.db.insertar("""
                INSERT INTO SIPEFI.TD_REL_VAL_PRACTICO (
                    id_solicitud, id_estatus_solicitud, id_valor_practico, busuario
                ) VALUES (
                    :id_solicitud, :id_estatus_solicitud, :id_valor_practico, :busuario
                )
            """, {
                "id_solicitud": self.id_solicitud,
                "id_estatus_solicitud": self.id_estatus,
                "id_valor_practico": val,
                "busuario": self.usuario
            })
        
    def _insertar_rel_licenciaturas(self, licenciaturas):
        for lic in licenciaturas:
            id_lic = lic["idLicenciatura"]
            semestres = lic.get("semestres", [])
            seriaciones_ant = lic.get("idSeriacionAnterior", [])
            seriaciones_cons = lic.get("idSeriacionConsecuente", [])
            
            # Si no hay seriaciones, usamos [0] como valor por defecto - Asignatura - Ninguna
            if not seriaciones_ant:
                seriaciones_ant = [0]
            if not seriaciones_cons:
                seriaciones_cons = [0]
            # Recorremos cada semestre y cada combinación de seriaciones
            for semestre in semestres:
                # Por si vienen como string del JSON, aseguramos int
                try:
                    semestre_val = int(semestre)
                except (TypeError, ValueError):
                    semestre_val = None
    
                if semestre_val is None:
                    continue
                
                # Si hay antecedentes y consecuentes, se inserta cada combinación
                for ant in seriaciones_ant:
                    for cons in seriaciones_cons:
                        self.db.insertar("""
                            INSERT INTO SIPEFI.TD_REL_LIC_ASIGNATURA (
                                id_solicitud, id_estatus_solicitud, id_licenciatura,
                                seriacion_ant, seriacion_cons, semestre, busuario
                            ) VALUES (
                                :id_solicitud, :id_estatus_solicitud, :id_lic,
                                :seriacion_ant, :seriacion_cons, :semestre, :busuario
                            )
                        """, {
                            "id_solicitud": self.id_solicitud,
                            "id_estatus_solicitud": self.id_estatus,
                            "id_lic": id_lic,
                            "seriacion_ant": ant,
                            "seriacion_cons": cons,
                            "semestre": semestre_val,
                            "busuario": self.usuario
                        })
                
    def _insertar_temario(self, temas):
        for tema in temas:
            self.db.insertar("""
                INSERT INTO SIPEFI.TD_TEMARIO_ASIGNATURA (
                    id_solicitud, id_estatus_solicitud, num_tema,
                    tema, objetivo, horas_tema, busuario
                ) VALUES (
                    :id_solicitud, :id_estatus_solicitud, :num_tema,
                    :tema, :objetivo, :horas_tema, :busuario
                )
            """, {
                "id_solicitud": self.id_solicitud,
                "id_estatus_solicitud": self.id_estatus,
                "num_tema": tema["numeroTema"],
                "tema": tema["nombre"],
                "objetivo": tema["objetivo"],
                "horas_tema": tema["horas"],
                "busuario": self.usuario
            })

    def _insertar_contenido(self, contenidos):
        for cont in contenidos:
            tema_relacionado = cont.get("temaRelacionado", "")
            num_tema = int(str(tema_relacionado).split('.')[0].strip())
            self.db.insertar("""
                INSERT INTO SIPEFI.TD_CONTENIDO_TEMATICO (
                    id_solicitud, id_estatus_solicitud, num_tema,
                    num_contenido, contenido, busuario
                ) VALUES (
                    :id_solicitud, :id_estatus_solicitud, :num_tema,
                    :num_contenido, :contenido, :busuario
                )
            """, {
                "id_solicitud": self.id_solicitud,
                "id_estatus_solicitud": self.id_estatus,
                "num_tema": num_tema,
                "num_contenido": cont["numeroCont"].split(".")[1],
                "contenido": cont["contenido"],
                "busuario": self.usuario
            })

    def _insertar_bibliografia(self, biblios):
        for i, bib in enumerate(biblios, start=1):  # ← comienza desde 1
            self.db.insertar("""
                INSERT INTO SIPEFI.TD_BIBLIOGRAFIA (
                    id_solicitud, id_estatus_solicitud, id_bibliografia,
                    es_complementaria, id_tipo_bibliografia, autor, publicacion,
                    titulo, campo_1, campo_2, campo_3, campo_4,
                    temas_recomienda, busuario
                ) VALUES (
                    :id_solicitud, :id_estatus_solicitud, :id_bibliografia,
                    :es_complementaria, :id_tipo_bibliografia, :autor, :publicacion,
                    :titulo, :campo_1, :campo_2, :campo_3, :campo_4,
                    :temas_recomienda, :busuario
                )
            """, {
                "id_solicitud": self.id_solicitud,
                "id_estatus_solicitud": self.id_estatus,
                "id_bibliografia": i,
                "es_complementaria": bib["clasifBiblio"],
                "id_tipo_bibliografia": bib["idTipo"],
                "autor": bib["autor"],
                "publicacion": bib["anio"],
                "titulo": bib["titulo"],
                "campo_1": bib["extra1"],
                "campo_2": bib["extra2"],
                "campo_3": bib["extra3"],
                "campo_4": bib["extra4"],
                "temas_recomienda": bib["temas"],
                "busuario": self.usuario
            })

    def _insertar_estrategias(self, estrategias):
        for _, formas in estrategias.get("formasEvaluacion", {}).items():
            for f in formas:
                self.db.insertar("""
                    INSERT INTO SIPEFI.TD_REL_ASIG_EVALUACION (
                        id_solicitud, id_estatus_solicitud, id_forma_eval, busuario
                    ) VALUES (
                        :id_solicitud, :id_estatus_solicitud, :id_forma_eval, :busuario
                    )
                """, {
                    "id_solicitud": self.id_solicitud,
                    "id_estatus_solicitud": self.id_estatus,
                    "id_forma_eval": f,
                    "busuario": self.usuario
                })
    
        for estrat in estrategias.get("estrategiasDidacticas", []):
            self.db.insertar("""
                INSERT INTO SIPEFI.TD_REL_ASIG_ESTRAT_DID (
                    id_solicitud, id_estatus_solicitud, id_estrategia_didact, busuario
                ) VALUES (
                    :id_solicitud, :id_estatus_solicitud, :id_estrategia_didact, :busuario
                )
            """, {
                "id_solicitud": self.id_solicitud,
                "id_estatus_solicitud": self.id_estatus,
                "id_estrategia_didact": estrat,
                "busuario": self.usuario
            })

    def _guardar_traza(self, comentario, estatus_origen, estatus_destino, accion="Guardado o Edición"):
        """
        Guarda un registro de traza en la historia de la solicitud.
    
        :param comentario: Comentario relacionado con la acción.
        :param estatus_origen: Estatus previo de la solicitud.
        :param estatus_destino: Estatus nuevo de la solicitud.
        :param accion: Texto que describe la acción realizada (Guardado, Aprobado, Rechazado, etc.).
        """
        self.db.insertar("""
            INSERT INTO SIPEFI.TD_HISTORIA_SOLICITUD (
                id_solicitud, id_estatus_origen, id_estatus_destino,
                comentario, accion, bfecha, busuario
            ) VALUES (
                :id_solicitud, :estatus_origen, :estatus_destino,
                :comentario, :accion, SYSDATE, :busuario
            )
        """, {
            "id_solicitud": self.id_solicitud,
            "estatus_origen": estatus_origen,
            "estatus_destino": estatus_destino,
            "comentario": comentario,
            "accion": accion,
            "busuario": self.usuario
        })

    def _actualizar_token(self):
        self.db.insertar("""
            UPDATE PARAMETRO.TP_ACCESOS
            SET estatus_acceso = 'E', fecha_acceso = SYSDATE
            WHERE token = :token
        """, {
            "token": self.token
        })

    def obtener_nombre_estatus(self, id_est):
        try:
            id_est = int(id_est)
        except (TypeError, ValueError):
            # Si no se puede convertir, forzamos al default
            return "Elaboración"
        return {
            0: "Cancelada",
            1: "Elaboración",
            2: "Revisión",
            3: "Concluida"
        }.get(id_est, "Elaboración")
        
    def dameDatosSolicitud(self, id_solicitud, id_estatus_solicitud, accion):
        """
        Reconstruye una solicitud con el numero de solicitud y su estatus.
        
        :param id_solicitud: ID único de la solicitud.
        :param id_estatus_solicitud: Estatus específico de la solicitud.
        :param accion: Parametro que indica la accion con la que se esta solicitando la informacion de la solicitud.
                **accion**
                1: Visualizar
                2: Editar
        :return: Diccionario con toda la información reconstruida de la solicitud.
        """
        resp = {}
        try:
            self.id_solicitud = id_solicitud
            self.id_estatus = id_estatus_solicitud
            params = {"id_solicitud": id_solicitud, "id_estatus_solicitud": id_estatus_solicitud}
        
            datos_generales = self.db.consulta("""
                SELECT 
                    a.asignatura, a.clave_asignatura, a.creditos, a.id_area_conocimiento, a.id_modalidad,
                    a.id_tipo_modalidad, a.id_caracter_asig, a.horas_teo_semana, a.horas_pract_semana,
                    a.horas_teo_semestre, a.horas_pract_semestre, a.objetivo_general, a.actividades_practicas,
                    a.formacion_integral, a.perfil_profesiografico, a.id_perfil,
                    u.usuario_sistema
                FROM SIPEFI.TD_SOLICITUD_TOMO_II a
                LEFT JOIN PARAMETRO.TP_USUARIO u ON a.ID_USUARIO_MOD = u.ID_USUARIO
                WHERE a.id_solicitud = :id_solicitud AND a.id_estatus_solicitud = :id_estatus_solicitud
            """, params)[0]
            
            valor_practico = self.db.consulta("""
                SELECT id_valor_practico
                FROM SIPEFI.TD_REL_VAL_PRACTICO
                WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :id_estatus_solicitud
            """, params)
            valor_practico_list = [row[0] for row in valor_practico]
            
            lics_raw = self.db.consulta("""
                SELECT id_licenciatura, seriacion_ant, seriacion_cons, semestre, id_solicitud
                FROM SIPEFI.TD_REL_LIC_ASIGNATURA
                WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :id_estatus_solicitud
            """, params)
            
            licenciaturas = {}
            for lic_id, s_ant, s_con, semestre, id_solicitud in lics_raw:
                key = (lic_id, id_solicitud)
                if key not in licenciaturas:
                    licenciaturas[key] = {
                        "idLic": lic_id,
                        "seriacionAnt": set(),
                        "seriacionCons": set(),
                        "semestres": set(),
                        "id_solicitud": id_solicitud
                    }
                if s_ant and s_ant != 0:
                    licenciaturas[key]["seriacionAnt"].add(s_ant)
                if s_con and s_con != 0:
                    licenciaturas[key]["seriacionCons"].add(s_con)
                if semestre and semestre != 0:
                    licenciaturas[key]["semestres"].add(semestre)
            
            # Convertir a lista y transformar sets en listas
            licenciaturas = [{
                "idLic": val["idLic"],
                "seriacionAnt": list(val["seriacionAnt"]),
                "seriacionCons": list(val["seriacionCons"]),
                "semestre": sorted(list(val["semestres"])),
                "idSolicitud":val["id_solicitud"],
            } for val in licenciaturas.values()]
        
            temario = self.db.consulta("""
                SELECT num_tema, tema, horas_tema, objetivo
                FROM SIPEFI.TD_TEMARIO_ASIGNATURA
                WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :id_estatus_solicitud
            """, params)
        
            contenido = self.db.consulta("""
                SELECT num_tema, num_tema||'.'||num_contenido, contenido
                FROM SIPEFI.TD_CONTENIDO_TEMATICO
                WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :id_estatus_solicitud
            """, params)
        
            bibliografia = self.db.consulta("""
                SELECT id_bibliografia, es_complementaria, id_tipo_bibliografia, autor,
                       publicacion, titulo, campo_1, campo_2, campo_3, campo_4, temas_recomienda
                FROM SIPEFI.TD_BIBLIOGRAFIA
                WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :id_estatus_solicitud
            """, params)
        
            formas_eval = self.db.consulta("""
                SELECT a.id_forma_eval, UPPER(TRIM(b.tipo_evaluacion))
                FROM SIPEFI.TD_REL_ASIG_EVALUACION a
                INNER JOIN CATALOGO.TC_FORMAS_EVALUACION b
                    ON a.id_forma_eval = b.id_forma_eval
                WHERE a.id_solicitud = :id_solicitud
                AND a.id_estatus_solicitud = :id_estatus_solicitud
            """, params)
            eval_diagnostica = []
            eval_formativa = []
            eval_sumativa = []
            
            for id_eval, tipo in formas_eval:
                tipo = tipo.lower()
                if tipo == 'diagnóstica':
                    eval_diagnostica.append(id_eval)
                elif tipo == 'formativa':
                    eval_formativa.append(id_eval)
                elif tipo == 'sumativa':
                    eval_sumativa.append(id_eval)
        
            estrategias_did = self.db.consulta("""
                SELECT id_estrategia_didact
                FROM SIPEFI.TD_REL_ASIG_ESTRAT_DID
                WHERE id_solicitud = :id_solicitud AND id_estatus_solicitud = :id_estatus_solicitud
            """, params)
            
            comentarios_raw = self.db.consulta("""
                SELECT busuario, TO_CHAR(bfecha, 'DD/MM/YYYY HH24:MI:SS') AS fecha, comentario
                FROM (
                    SELECT 
                        h.busuario,
                        h.bfecha,
                        h.comentario,
                        ROW_NUMBER() OVER (
                            PARTITION BY h.id_solicitud, h.id_estatus_origen, h.id_estatus_destino, h.busuario
                            ORDER BY h.bfecha DESC
                        ) AS rn
                    FROM SIPEFI.TD_HISTORIA_SOLICITUD h
                    WHERE h.id_solicitud = :id_solicitud AND LENGTH(h.comentario) > 0
                )
                WHERE rn = 1
                ORDER BY fecha DESC
            """, {"id_solicitud": id_solicitud})
            comentarios = []
            for row in comentarios_raw:
                comentario_val = row[2]
                if hasattr(comentario_val, "read"):
                    comentario_val = comentario_val.read()
                comentarios.append({
                    "usuario": row[0],
                    "fecha": row[1],
                    "comentario": str(comentario_val) if comentario_val is not None else ""
                })

            # === Armar objeto ===
        
            resp = {
                "datosGenerales": {
                    "asignatura": datos_generales[0],
                    "claveAsignatura": datos_generales[1],
                    "creditos": datos_generales[2],
                    "areaConocimiento": datos_generales[3],
                    "modalidad": datos_generales[4],
                    "tipoModalidad": datos_generales[5],
                    "caracterAsignatura": datos_generales[6],
                    "hSemTeoria": datos_generales[7],
                    "hSemPractica": datos_generales[8],
                    "hSemestreTeoria": datos_generales[9],
                    "hSemestrePractica": datos_generales[10],
                    "objAsig": datos_generales[11].read() if hasattr(datos_generales[11], "read") else datos_generales[11]
                },
                "valorPractico": valor_practico_list,
                "actPracticas": datos_generales[12],
                "relacionLicenciaturas": licenciaturas,
                "temario": [{
                    "numeroTema": tem[0],
                    "nombre": tem[1],
                    "horas": tem[2],
                    "objetivo": tem[3]
                } for tem in temario],
                "contenido": [{
                    "temaRelacionado": cont[0],
                    "numeroCont": cont[1],
                    "contenido": cont[2]
                } for cont in contenido],
                "bibliografia": [{
                    "id": bib[0],
                    "clasifBiblio": bib[1],
                    "idTipo": bib[2],
                    "autor": bib[3],
                    "anio": bib[4],
                    "titulo": bib[5],
                    "extra1": bib[6],
                    "extra2": bib[7],
                    "extra3": bib[8],
                    "extra4": bib[9],
                    "temas": bib[10]
                } for bib in bibliografia],
                "estrategiasEvaluacion": {
                    "formasEvaluacion": {
                        "diagnostica": eval_diagnostica,
                        "formativa": eval_formativa,
                        "sumativa": eval_sumativa
                    },
                    "estrategiasDidacticas": [e[0] for e in estrategias_did],
                    "formacionIntegral": datos_generales[13],
                    "perfilProfesiografico": datos_generales[14]
                },
                "idEstSoli": id_estatus_solicitud,
                "numSolicitud": id_solicitud,
                "nomEstSoli": self.obtener_nombre_estatus(id_estatus_solicitud),
                "usuarioSoli": datos_generales[16],
                "rol": datos_generales[15],
                "comentarios": comentarios,
                "accion": accion,
                "estatus": 200
            }
        except ValueError:
            resp = { "estatus": 204 }
        return resp
    
    def cancelaSolicitud(self, idSol, idEst, token, rol, usuario, comentario):
        """
        Cancela la solicitud (estatus 0) solo si su id_asignatura (idSol) NO está
        referenciado como seriación en ninguna fila de SIPEFI.TD_REL_LIC_ASIGNATURA.
        Tras cancelar, elimina la asignatura en SIPEFI.TD_ASIGNATURA.
    
        :param idSol: ID de la solicitud (también id_asignatura).
        :param idEst: Estatus actual.
        :param token: Token del usuario.
        :param rol: Rol del usuario (se puede usar para id_perfil en estatus 0).
        :param usuario: Usuario que ejecuta la cancelación.
        :param comentario: Motivo de cancelación.
        :return: Diccionario con estatus resultante.
        """
        try:
            self.id_solicitud = int(idSol)
            self.id_estatus   = int(idEst)
            self.usuario      = usuario
            self.token        = token
            rol               = int(rol)
            
            # 0) Validación de integridad: la asignatura NO debe estar referenciada como seriación ===
            total_refs = self.db.consulta("""
                SELECT COUNT(*)
                FROM SIPEFI.TD_REL_LIC_ASIGNATURA
                WHERE seriacion_ant = :id_asig OR seriacion_cons = :id_asig
            """, {"id_asig": self.id_solicitud})[0][0]
    
            if total_refs > 0:
                # 409: Conflicto – Hay dependencias
                raise Exception((
                    409,
                    f"No se puede cancelar la solicitud <strong>SIPEFI-{self.id_solicitud}</strong>. "
                    f"La asignatura está referenciada como seriación en <strong>{total_refs} registro(s).</strong>"
                ))
    
            # Si ya está cancelada, solo registra traza y cierra token
            if self.id_estatus == 0:
                self._guardar_traza(comentario, 0, 0, "Cancelada (ya estaba en 0)")
                self._actualizar_token()
                return {"idS": self.id_solicitud, "idES": 0, "nomES": "Cancelada"}
    
            id_usuario_mod = self.db.getIdUsuario(self.usuario)
    
            # 1) Marcar versión actual como histórica
            self.db.insertar("""
                UPDATE SIPEFI.TD_SOLICITUD_TOMO_II
                   SET historica = 1,
                       fecha_modificacion = SYSDATE,
                       id_usuario_mod = :id_usuario_mod
                 WHERE id_solicitud = :id_solicitud
                   AND id_estatus_solicitud = :id_estatus
            """, {
                "id_usuario_mod": id_usuario_mod,
                "id_solicitud": self.id_solicitud,
                "id_estatus": self.id_estatus
            })
    
            # 2) Limpiar cualquier residuo en estatus destino (0 = Cancelada)
            self.limpiar_solicitud(self.id_solicitud, 0)
    
            # 3) Clonar versión actual hacia estatus 0
            self._clonar_version(self.id_solicitud, self.id_estatus, 0, self.usuario)
    
            # 4) Ajustar id_perfil en la versión cancelada al rol que ejecuta
            self.db.insertar("""
                UPDATE SIPEFI.TD_SOLICITUD_TOMO_II
                   SET id_perfil = :rol
                 WHERE id_solicitud = :id_solicitud
                   AND id_estatus_solicitud = 0
            """, {
                "rol": rol,
                "id_solicitud": self.id_solicitud
            })
    
            # 5) Guardar traza y cerrar token
            self._guardar_traza(comentario, self.id_estatus, 0, "Cancelada")
            self._actualizar_token()
            
            # 6) Eliminar la asignatura del catálogo de asignatura
            self.db.insertar("""
                DELETE FROM SIPEFI.TD_ASIGNATURA
                WHERE id_asignatura = :id_asig
            """, {"id_asig": self.id_solicitud})
            
            return {"idS": self.id_solicitud, "idES": 0, "nomES": "Cancelada"}
    
        except Exception:
            raise
