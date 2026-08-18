# -*- coding: utf-8 -*-
import logging
from functools import lru_cache
from pathlib import Path

from sipefi_apps.principal.modelo.ConexionBD import ConexionBD as conBD

logger = logging.getLogger(__name__)


def _lob_a_texto(valor):
    if valor is None:
        return ""
    if hasattr(valor, "read"):
        try:
            return valor.read() or ""
        except Exception:
            logger.exception("No fue posible leer un CLOB para el PDF de Formación complementaria.")
            return ""
    return str(valor)


class ConsultasPDFFormacionComplementaria:
    def __init__(self):
        self.sql_dir = Path(__file__).parent / "sql"

    @staticmethod
    @lru_cache(maxsize=16)
    def _read_sql_file(path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError(f"No se encontró el archivo SQL: {path}")
        return path.read_text(encoding="utf-8")

    def _load_sql(self, filename: str) -> str:
        return self._read_sql_file(self.sql_dir / filename)

    @staticmethod
    def _cursor():
        return conBD().cursorBD()

    def get_informacion(self, id_formacion: int, id_usuario: int):
        cursor = self._cursor()
        try:
            cursor.execute(
                self._load_sql("getInformacionFormacion.sql"),
                {"id_formacion": int(id_formacion), "id_usuario": int(id_usuario)},
            )
            row = cursor.fetchone()
            if not row:
                return None
            columnas = [col[0].lower() for col in cursor.description]
            data = dict(zip(columnas, row))
            data["objetivo_general"] = _lob_a_texto(data.get("objetivo_general"))
            data["justificacion_academica"] = _lob_a_texto(data.get("justificacion_academica"))
            return data
        finally:
            cursor.close()

    def get_temario(self, id_formacion: int):
        cursor = self._cursor()
        try:
            cursor.execute(self._load_sql("getTemario.sql"), {"id_formacion": int(id_formacion)})
            columnas = [col[0].lower() for col in cursor.description]
            return [dict(zip(columnas, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def get_bibliografia(self, id_formacion: int):
        cursor = self._cursor()
        try:
            cursor.execute(self._load_sql("getBibliografia.sql"), {"id_formacion": int(id_formacion)})
            columnas = [col[0].lower() for col in cursor.description]
            return [dict(zip(columnas, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()

    def get_estrategias(self, id_formacion: int):
        cursor = self._cursor()
        try:
            cursor.execute(self._load_sql("getEstrategias.sql"), {"id_formacion": int(id_formacion)})
            columnas = [col[0].lower() for col in cursor.description]
            return [dict(zip(columnas, row)) for row in cursor.fetchall()]
        finally:
            cursor.close()
