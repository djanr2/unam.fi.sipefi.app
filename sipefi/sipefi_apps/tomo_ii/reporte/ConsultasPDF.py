import secrets
from pathlib import Path
from functools import lru_cache

from sipefi_apps.principal.modelo.ConexionBD import ConexionBD as conBD

class ConsultasPDF():

    def __init__(self):
        """
            Funcion que ayuda a inicializar parametros y valores necesarios para las consultas SQL.
        """
        self.rol = ""
        self.idUniverso = ""
        # Carpeta donde guardarás tus .sql (ajusta la ruta a tu estructura real)
        # Ejemplo: este archivo está en sipefi_apps/principal/modelo/consultas_pdf.py
        # y los .sql en sipefi_apps/principal/modelo/sql/
        self.sql_dir = Path(__file__).parent / "sql"

    @staticmethod
    @lru_cache(maxsize=64)
    def _read_sql_file(path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el archivo SQL: {path}")
        return path.read_text(encoding="utf-8")



    def _load_sql(self, filename: str) -> str:
        """
        Carga y devuelve el contenido del archivo SQL.
        Usa caché para evitar lecturas repetidas de disco.
        """
        sql_path = self.sql_dir / filename
        return self._read_sql_file(sql_path)

    def get_informacion_asignatura(self, id_licenciatura: int, id_asignatura: int):
        sql = self._load_sql("getInformacionAsignatura.sql")
        cursor = conBD().cursorBD()
        try:
            cursor.execute(sql, {"id_licenciatura": id_licenciatura, "id_asignatura": id_asignatura})
            res = cursor.fetchall()
        except Exception as e:
            print(f"Error en getLicenciatura archivo de consulta: {e}")
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
            print(f"Error en getSeriaciones archivo de consulta: {e}")
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
            print(f"Error en getTemario archivo de consulta: {e}")
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
            print(f"Error en getTemario archivo de consulta: {e}")
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
            print(f"Error en getSubtemas archivo de consulta: {e}")
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
            print(f"Error en getBibliografiaBasica archivo de consulta: {e}")
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
            print(f"Error en getBibliografiaComplementaria archivo de consulta: {e}")
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
            print(f"Error en getEstrategiasDidacticas archivo de consulta: {e}")
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
            print(f"Error en getFormasEvaluacion archivo de consulta: {e}")
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
            print(f"Error en getDocumentoOficialByRol archivo de consulta: {e}")
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
            print(f"Error en getIdsAsignatura archivo de consulta: {e}")
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
            print(f"Error en getIdsAsignatura archivo de consulta: {e}")
            res = []
        finally:
            cursor.close()
        return res


