"""
Configuración centralizada de la aplicación.
Variables de entorno y parámetros de conexión.
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ==========================================
# Configuración de Base de Datos PostgreSQL
# ==========================================
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")) if os.getenv("DB_PORT") else 2345,
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# String de conexión para psycopg2
DB_CONNECTION_STRING = (
    f"postgresql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}"
    f"@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
)

# ==========================================
# Configuración General
# ==========================================
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
TIMEZONE = os.getenv("TIMEZONE", "UTC")
