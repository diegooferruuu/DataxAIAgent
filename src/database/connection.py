"""
Gestión de conexiones a PostgreSQL.
Provee métodos para conectar, desconectar y ejecutar queries.
"""

import psycopg2
from psycopg2 import sql, extras
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import logging

from src.config.settings import DATABASE_CONFIG

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    Gestor centralizado de conexiones a PostgreSQL.
    Maneja la conexión, ejecución de queries y cierre de conexiones.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa el gestor de conexión.

        Args:
            config: Diccionario con los parámetros de conexión.
                   Si no se proporciona, usa DATABASE_CONFIG de settings.
        """
        self.config = config or DATABASE_CONFIG
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """
        Establece la conexión con PostgreSQL.

        Returns:
            bool: True si la conexión fue exitosa, False en caso contrario.
        """
        try:
            self.connection = psycopg2.connect(
                host=self.config["host"],
                port=self.config["port"],
                database=self.config["database"],
                user=self.config["user"],
                password=self.config["password"],
            )
            logger.info(
                f"Conexión exitosa a PostgreSQL: {self.config['database']} "
                f"en {self.config['host']}:{self.config['port']}"
            )
            return True
        except psycopg2.Error as e:
            logger.error(f"Error al conectar a PostgreSQL: {e}")
            return False

    def disconnect(self) -> bool:
        """
        Cierra la conexión con PostgreSQL.

        Returns:
            bool: True si se cerró exitosamente, False en caso contrario.
        """
        try:
            if self.connection:
                self.connection.close()
                logger.info("Conexión a PostgreSQL cerrada.")
                return True
        except psycopg2.Error as e:
            logger.error(f"Error al cerrar la conexión: {e}")
        return False

    @contextmanager
    def get_cursor(self, dictionary: bool = False):
        """
        Context manager para obtener un cursor.

        Args:
            dictionary: Si True, retorna resultados como diccionarios.

        Yields:
            cursor: Cursor de psycopg2.
        """
        cursor_class = extras.RealDictCursor if dictionary else psycopg2.extensions.cursor
        cursor = self.connection.cursor(cursor_factory=cursor_class)
        try:
            yield cursor
        finally:
            cursor.close()

    def execute_query(
        self, query: str, params: Optional[tuple] = None
    ) -> bool:
        """
        Ejecuta una query sin retornar resultados (INSERT, UPDATE, DELETE).

        Args:
            query: String de SQL.
            params: Parámetros para la query (evita SQL injection).

        Returns:
            bool: True si se ejecutó exitosamente, False en caso contrario.
        """
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
            self.connection.commit()
            logger.debug(f"Query ejecutada correctamente: {query[:50]}...")
            return True
        except psycopg2.Error as e:
            self.connection.rollback()
            logger.error(f"Error ejecutando query: {e}")
            return False

    def fetch_one(
        self, query: str, params: Optional[tuple] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Ejecuta una query y retorna un solo resultado como diccionario.

        Args:
            query: String de SQL.
            params: Parámetros para la query.

        Returns:
            Diccionario con los datos o None si no hay resultados.
        """
        try:
            with self.get_cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                result = cursor.fetchone()
            return result
        except psycopg2.Error as e:
            logger.error(f"Error en fetch_one: {e}")
            return None

    def fetch_all(
        self, query: str, params: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta una query y retorna todos los resultados como diccionarios.

        Args:
            query: String de SQL.
            params: Parámetros para la query.

        Returns:
            Lista de diccionarios con los datos.
        """
        try:
            with self.get_cursor(dictionary=True) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
            return results if results else []
        except psycopg2.Error as e:
            logger.error(f"Error en fetch_all: {e}")
            return []

    def execute_many(
        self, query: str, data: List[tuple]
    ) -> bool:
        """
        Ejecuta una query múltiples veces con diferentes parámetros
        (batch insert/update).

        Args:
            query: String de SQL.
            data: Lista de tuplas con parámetros para cada ejecución.

        Returns:
            bool: True si se ejecutó exitosamente, False en caso contrario.
        """
        try:
            with self.get_cursor() as cursor:
                cursor.executemany(query, data)
            self.connection.commit()
            logger.info(f"Batch de {len(data)} registros procesado exitosamente.")
            return True
        except psycopg2.Error as e:
            self.connection.rollback()
            logger.error(f"Error en batch insert/update: {e}")
            return False
