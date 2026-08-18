import secrets
import logging
from pathlib import Path
from functools import lru_cache

from sipefi_apps.principal.modelo.ConexionBD import ConexionBD as conBD

logger = logging.getLogger(__name__)

class ConsultasPDF():

    def __init__(self):
        """
            Funcion que ayuda a inicializar parametros y valores necesarios para las consultas SQL.
        """
        self.rol = ""
        self.idUniverso = ""
        # Carpeta donde guardaras tus .sql (ajusta la ruta a tu estructura real)
        # Ejemplo: este archivo esta en sipefi_apps/principal/modelo/consultas_pdf.py
        # y los .sql en sipefi_apps/principal/modelo/sql/
        self.sql_dir = Path(__file__).parent / "sql"

    @staticmethod
    @lru_cache(maxsize=64)
    def _read_sql_file(path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError(f"No se encontro el archivo SQL: {path}")
        return path.read_text(encoding="utf-8")



    def _load_sql(self, filename: str) -> str:
        """
        Carga y devuelve el contenido del archivo SQL.
        Usa cache para evitar lecturas repetidas de disco.
        """
        sql_path = self.sql_dir / filename
        return self._read_sql_file(sql_path)


    def get_estatus_activo_para_pdf(self, id_asignatura: int):
        """
        Devuelve el único estatus activo de una solicitud si es apto para PDF.

        Reglas:
        - Debe existir exactamente una version con HISTORICA = 0.
        - El estatus activo no puede ser 0 (solicitud cancelada).
        """
        cursor = conBD().cursorBD()
        try:
            cursor.execute("""
                SELECT ID_ESTATUS_SOLICITUD
                  FROM SIPEFI.TD_SOLICITUD_TOMO_II
                 WHERE ID_SOLICITUD = :id_asignatura
                   AND HISTORICA = 0
            """, {"id_asignatura": int(id_asignatura)})
            rows = cursor.fetchall()

            if len(rows) != 1:
                return None

            estatus = int(rows[0][0])
            return estatus if estatus != 0 else None
        finally:
            cursor.close()

    def get_informacion_asignatura(self, id_licenciatura: int, id_asignatura: int):
        sql = self._load_sql("getInformacionAsignatura.sql")
        cursor = conBD().cursorBD()
        try:
            cursor.execute(sql, {"id_licenciatura": id_licenciatura, "id_asignatura": id_asignatura})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: get_informacion_asignatura")
            res = []
        finally:
            cursor.close()
        return res

    def get_seriaciones(self, id_licenciatura: int, id_asignatura: int):
        sql = self._load_sql("getSeriaciones.sql")
        cursor = conBD().cursorBD()
        try:
            cursor.execute(sql, {"id_licenciatura": id_licenciatura, "id_asignatura": id_asignatura})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: get_seriaciones")
            res = []
        finally:
            cursor.close()
        return res

    def get_temario(self, id_asignatura: int):
        sql = self._load_sql("getTemario.sql")
        cursor = conBD().cursorBD()
        try:
            cursor.execute(sql, {"id_asignatura": id_asignatura})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: temario/resumen")
            res = []
        finally:
            cursor.close()
        return res

    def get_resumen_temario(self, id_asignatura: int):
        sql = self._load_sql("getResumenTemario.sql")
        cursor = conBD().cursorBD()
        try:
            cursor.execute(sql, {"id_asignatura": id_asignatura})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: temario/resumen")
            res = []
        finally:
            cursor.close()
        return res

    def get_subtemas(self, id_asignatura: int):
        sql = self._load_sql("getSubtemas.sql")
        cursor = conBD().cursorBD()
        try:
            cursor.execute(sql, {"id_asignatura": id_asignatura})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: get_subtemas")
            res = []
        finally:
            cursor.close()
        return res

    def get_bibliografia_basica(self, id_asignatura: int):
        sql = self._load_sql("getBibliografiaBasica.sql")
        cursor = conBD().cursorBD()
        try:
            cursor.execute(sql, {"id_asignatura": id_asignatura})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: get_bibliografia_basica")
            res = []
        finally:
            cursor.close()
        return res

    def get_bibliografia_complementaria(self, id_asignatura: int):
        sql = self._load_sql("getBibliografiaComplementaria.sql")
        cursor = conBD().cursorBD()
        try:
            cursor.execute(sql, {"id_asignatura": id_asignatura})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: get_bibliografia_complementaria")
            res = []
        finally:
            cursor.close()
        return res

    def get_estrategias_didacticas(self, id_asignatura: int):
        sql = self._load_sql("getEstrategiasDidacticas.sql")
        cursor = conBD().cursorBD()
        try:
            cursor.execute(sql, {"id_asignatura": id_asignatura})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: get_estrategias_didacticas")
            res = []
        finally:
            cursor.close()
        return res

    def get_formas_evaluacion(self, id_asignatura: int, id_forma_evaluacion: str):
        sql = self._load_sql("getFormasEvaluacion.sql")
        cursor = conBD().cursorBD()
        try:
            cursor.execute(sql, {"id_asignatura": id_asignatura, "id_forma_evaluacion": id_forma_evaluacion})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: get_formas_evaluacion")
            res = []
        finally:
            cursor.close()
        return res


    def get_is_documento_ofical_by_perfil(self, id_perfil: int):
        sql = self._load_sql("getDocumentoOficialByRol.sql")
        cursor = conBD().cursorBD()
        str_validador = "Validador%"
        str_administrador = "Administrador%"
        str_coordinador = "Coordinador%"
        try:
            cursor.execute(sql, {"id_perfil": id_perfil,"str_validador": str_validador,"str_administrador": str_administrador, "str_coordinador": str_coordinador})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: get_documento_oficial_by_rol")
            res = []
        finally:
            cursor.close()
        return res

    def get_ids_asignaturas_obligatorias_ordered_by_semestre_name(self, id_licenciatura: int):
        sql = self._load_sql("getIdsAsignatura.sql")
        cursor = conBD().cursorBD()
        caracter = 1;
        try:
            cursor.execute(sql, {"id_licenciatura": id_licenciatura,"caracter": caracter})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: get_ids_asignatura")
            res = []
        finally:
            cursor.close()
        return res

    def get_ids_asignaturas_optativas_ordered_by_semestre_name(self, id_licenciatura: int):
        sql = self._load_sql("getIdsAsignatura.sql")
        cursor = conBD().cursorBD()
        caracter = 2;
        try:
            cursor.execute(sql, {"id_licenciatura": id_licenciatura,"caracter": caracter})
            res = cursor.fetchall()
        except Exception as e:
            logger.exception("Error en consulta PDF: get_ids_asignatura")
            res = []
        finally:
            cursor.close()
        return res


