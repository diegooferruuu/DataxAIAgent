"""
Lógica de subida de datos a PostgreSQL.
Maneja inserciones, actualizaciones y validaciones para las tablas file y report.
"""

from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

from src.database.connection import DatabaseConnection

logger = logging.getLogger(__name__)


class FileUploader:
    """
    Gestor de subida de datos a la tabla 'file'.
    """

    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el uploader de archivos.

        Args:
            db_connection: Instancia de DatabaseConnection.
        """
        self.db = db_connection
        self.table_name = "file"

    def insert_file(self, file_data: Dict[str, Any]) -> Optional[int]:
        """
        Inserta un nuevo registro en la tabla 'file'.

        Args:
            file_data: Diccionario con los datos del archivo.
                      Claves esperadas: id_file, id_source, name, code, main_url, etc.

        Returns:
            int: id_file del registro insertado, None si falla.
        """
        # Define el orden de columnas esperadas basado en el schema
        columns = [
            "id_file", "id_source", "name", "code", "main_url", "path",
            "type", "specific_url", "alternate_url", "navigation_path",
            "publication_frequency", "priority", "state", "creation_date",
            "update_date", "observations", "updated_to", "last_file_path",
            "last_file_url", "schedule_interval", "publication_date",
            "key_words", "section_path", "short_name", "download_type"
        ]

        # Construir la query dinámicamente
        values = []
        placeholders = []

        for col in columns:
            if col in file_data:
                values.append(file_data[col])
                placeholders.append("%s")

        if not values:
            logger.error("No hay datos válidos para insertar en la tabla 'file'.")
            return None

        active_columns = [col for col in columns if col in file_data]
        columns_str = ", ".join(active_columns)
        placeholders_str = ", ".join(placeholders)

        query = f"""
            INSERT INTO {self.table_name} ({columns_str})
            VALUES ({placeholders_str})
            RETURNING id_file;
        """

        try:
            result = self.db.fetch_one(query, tuple(values))
            if result:
                file_id = result.get("id_file")
                logger.info(f"Archivo insertado exitosamente con ID: {file_id}")
                return file_id
            else:
                logger.error("No se retornó ID después de la inserción.")
                return None
        except Exception as e:
            logger.error(f"Error al insertar archivo: {e}")
            return None

    def update_file(self, file_id: int, file_data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro existente en la tabla 'file'.

        Args:
            file_id: ID del archivo a actualizar.
            file_data: Diccionario con los datos a actualizar.

        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.
        """
        if not file_data:
            logger.warning("No hay datos para actualizar.")
            return False

        # Construir la query de UPDATE dinámicamente
        set_clauses = []
        values = []

        for key, value in file_data.items():
            set_clauses.append(f"{key} = %s")
            values.append(value)

        # Añadir el id al final para la cláusula WHERE
        values.append(file_id)

        set_str = ", ".join(set_clauses)
        query = f"UPDATE {self.table_name} SET {set_str} WHERE id_file = %s;"

        try:
            success = self.db.execute_query(query, tuple(values))
            if success:
                logger.info(f"Archivo ID {file_id} actualizado exitosamente.")
            return success
        except Exception as e:
            logger.error(f"Error al actualizar archivo ID {file_id}: {e}")
            return False

    def upsert_file(
        self, file_data: Dict[str, Any], update_fields: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Realiza un INSERT ... ON CONFLICT UPDATE (upsert).
        Si el id_file ya existe, actualiza los campos especificados.

        Args:
            file_data: Diccionario con los datos del archivo (debe incluir id_file).
            update_fields: Lista de campos a actualizar en caso de conflicto.
                          Si es None, actualiza todos excepto id_file.

        Returns:
            int: id_file del registro, None si falla.
        """
        if "id_file" not in file_data:
            logger.error("id_file es obligatorio para upsert.")
            return None

        # Campos que están presentes en file_data
        columns = list(file_data.keys())
        placeholders = ["%s"] * len(columns)
        columns_str = ", ".join(columns)
        placeholders_str = ", ".join(placeholders)

        # Campos a actualizar (por defecto todos excepto id_file)
        if update_fields is None:
            update_fields = [col for col in columns if col != "id_file"]

        # Construir la cláusula ON CONFLICT
        update_pairs = [f"{col} = EXCLUDED.{col}" for col in update_fields]
        update_str = ", ".join(update_pairs)

        query = f"""
            INSERT INTO {self.table_name} ({columns_str})
            VALUES ({placeholders_str})
            ON CONFLICT (id_file)
            DO UPDATE SET {update_str}
            RETURNING id_file;
        """

        try:
            result = self.db.fetch_one(query, tuple(file_data.values()))
            if result:
                file_id = result.get("id_file")
                logger.info(f"Archivo upsertado con ID: {file_id}")
                return file_id
            else:
                logger.error("No se retornó ID después del upsert.")
                return None
        except Exception as e:
            logger.error(f"Error en upsert de archivo: {e}")
            return None

    def batch_insert_files(self, files_data: List[Dict[str, Any]]) -> Tuple[int, int]:
        """
        Inserta múltiples registros en la tabla 'file' en un batch.

        Args:
            files_data: Lista de diccionarios con datos de archivos.

        Returns:
            Tuple (insertados_exitosos, insertados_fallidos)
        """
        successful = 0
        failed = 0

        for file_data in files_data:
            result = self.insert_file(file_data)
            if result:
                successful += 1
            else:
                failed += 1

        logger.info(
            f"Batch insert completado: {successful} exitosos, {failed} fallidos."
        )
        return successful, failed


class ReportUploader:
    """
    Gestor de subida de datos a la tabla 'report'.
    """

    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializa el uploader de reportes.

        Args:
            db_connection: Instancia de DatabaseConnection.
        """
        self.db = db_connection
        self.table_name = "report"

    def insert_report(self, report_data: Dict[str, Any]) -> Optional[int]:
        """
        Inserta un nuevo registro en la tabla 'report'.

        Args:
            report_data: Diccionario con los datos del reporte.
                        Claves esperadas: id_report, id_file, name, etc.

        Returns:
            int: id_report del registro insertado, None si falla.
        """
        # Define las columnas esperadas
        columns = [
            "id_report", "id_file", "name", "publication_data", 
            "publication_frequency", "creation_date", "update_date",
            "observations", "code", "path", "converted_report_path",
            "converted_to", "key_words", "type", "isActive",
            "storage_table", "file_extension", "replacement_table",
            "compare_dates", "page_number", "decimal_separator",
            "conversion_factor", "migrated_to", "load_scope",
            "text_normalization"
        ]

        # Construir la query dinámicamente
        values = []
        active_columns = []

        for col in columns:
            if col in report_data:
                values.append(report_data[col])
                active_columns.append(col)

        if not values:
            logger.error("No hay datos válidos para insertar en la tabla 'report'.")
            return None

        columns_str = ", ".join(active_columns)
        placeholders_str = ", ".join(["%s"] * len(values))

        query = f"""
            INSERT INTO {self.table_name} ({columns_str})
            VALUES ({placeholders_str})
            RETURNING id_report;
        """

        try:
            result = self.db.fetch_one(query, tuple(values))
            if result:
                report_id = result.get("id_report")
                logger.info(f"Reporte insertado exitosamente con ID: {report_id}")
                return report_id
            else:
                logger.error("No se retornó ID después de la inserción.")
                return None
        except Exception as e:
            logger.error(f"Error al insertar reporte: {e}")
            return None

    def update_report(self, report_id: int, report_data: Dict[str, Any]) -> bool:
        """
        Actualiza un registro existente en la tabla 'report'.

        Args:
            report_id: ID del reporte a actualizar.
            report_data: Diccionario con los datos a actualizar.

        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.
        """
        if not report_data:
            logger.warning("No hay datos para actualizar.")
            return False

        # Construir la query de UPDATE dinámicamente
        set_clauses = []
        values = []

        for key, value in report_data.items():
            set_clauses.append(f"{key} = %s")
            values.append(value)

        # Añadir el id al final para la cláusula WHERE
        values.append(report_id)

        set_str = ", ".join(set_clauses)
        query = f"UPDATE {self.table_name} SET {set_str} WHERE id_report = %s;"

        try:
            success = self.db.execute_query(query, tuple(values))
            if success:
                logger.info(f"Reporte ID {report_id} actualizado exitosamente.")
            return success
        except Exception as e:
            logger.error(f"Error al actualizar reporte ID {report_id}: {e}")
            return False

    def upsert_report(
        self, report_data: Dict[str, Any], update_fields: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Realiza un INSERT ... ON CONFLICT UPDATE (upsert).
        Si el id_report ya existe, actualiza los campos especificados.

        Args:
            report_data: Diccionario con los datos del reporte (debe incluir id_report).
            update_fields: Lista de campos a actualizar en caso de conflicto.
                          Si es None, actualiza todos excepto id_report.

        Returns:
            int: id_report del registro, None si falla.
        """
        if "id_report" not in report_data:
            logger.error("id_report es obligatorio para upsert.")
            return None

        # Campos presentes en report_data
        columns = list(report_data.keys())
        placeholders = ["%s"] * len(columns)
        columns_str = ", ".join(columns)
        placeholders_str = ", ".join(placeholders)

        # Campos a actualizar (por defecto todos excepto id_report)
        if update_fields is None:
            update_fields = [col for col in columns if col != "id_report"]

        # Construir la cláusula ON CONFLICT
        update_pairs = [f"{col} = EXCLUDED.{col}" for col in update_fields]
        update_str = ", ".join(update_pairs)

        query = f"""
            INSERT INTO {self.table_name} ({columns_str})
            VALUES ({placeholders_str})
            ON CONFLICT (id_report)
            DO UPDATE SET {update_str}
            RETURNING id_report;
        """

        try:
            result = self.db.fetch_one(query, tuple(report_data.values()))
            if result:
                report_id = result.get("id_report")
                logger.info(f"Reporte upsertado con ID: {report_id}")
                return report_id
            else:
                logger.error("No se retornó ID después del upsert.")
                return None
        except Exception as e:
            logger.error(f"Error en upsert de reporte: {e}")
            return None

    def batch_insert_reports(
        self, reports_data: List[Dict[str, Any]]
    ) -> Tuple[int, int]:
        """
        Inserta múltiples registros en la tabla 'report' en un batch.

        Args:
            reports_data: Lista de diccionarios con datos de reportes.

        Returns:
            Tuple (insertados_exitosos, insertados_fallidos)
        """
        successful = 0
        failed = 0

        for report_data in reports_data:
            result = self.insert_report(report_data)
            if result:
                successful += 1
            else:
                failed += 1

        logger.info(
            f"Batch insert reportes completado: {successful} exitosos, {failed} fallidos."
        )
        return successful, failed
