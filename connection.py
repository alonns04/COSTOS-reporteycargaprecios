import logging
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import pandas as pd

try:
    import pyodbc
except ImportError:  # pragma: no cover - depende del entorno
    pyodbc = None


BASE_DIR = Path(__file__).resolve().parent

SERVER = os.getenv("SQL_SERVER", "").strip()
PORT = os.getenv("SQL_PORT", "").strip()
DATABASE = os.getenv("SQL_DATABASE", "").strip()
USER = os.getenv("SQL_USER", "").strip()
PWD = os.getenv("SQL_PASSWORD", "").strip()
ODBC_DRIVER = os.getenv("ODBC_DRIVER", "SQL Server Native Client 11.0").strip()
USE_SQLITE = os.getenv("USE_SQLITE", "true").strip().lower() in {"1", "true", "yes", "y", "si", "sí"}
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(BASE_DIR / "costos.db")).strip()


def obtener_ruta_sqlite() -> Path:
    """Devuelve la ruta absoluta del archivo SQLite, creando el directorio si hace falta."""
    sqlite_path = Path(SQLITE_DB_PATH).expanduser()
    if not sqlite_path.is_absolute():
        sqlite_path = BASE_DIR / sqlite_path
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite_path


def construir_cadena_conexion() -> str:
    """Construye la cadena de conexión usando variables de entorno."""
    if USE_SQLITE:
        return SQLITE_DB_PATH

    if not SERVER or not DATABASE:
        raise RuntimeError("Faltan variables de entorno: SQL_SERVER o SQL_DATABASE")

    server = f"{SERVER},{PORT}" if PORT else SERVER
    if USER and PWD:
        auth = f"UID={USER};PWD={PWD};"
    else:
        auth = "Trusted_Connection=yes;"
    return f"DRIVER={{{ODBC_DRIVER}}};SERVER={server};DATABASE={DATABASE};{auth}"


def obtener_conexion():
    """Devuelve una conexión lista para usar, ya sea SQLite o una base SQL Server."""
    if USE_SQLITE:
        sqlite_path = obtener_ruta_sqlite()
        logging.getLogger(__name__).info(f"Conectando a SQLite local: {sqlite_path}")
        return sqlite3.connect(str(sqlite_path))

    if pyodbc is None:
        raise RuntimeError("pyodbc no está instalado y no se está usando SQLite.")

    conn_str = construir_cadena_conexion()
    logging.getLogger(__name__).info(f"Creando conexión a la base de datos: {conn_str}")
    return pyodbc.connect(conn_str)


@contextmanager
def conexion_contextual():
    """Permite usar: with conexion_contextual() as conn:"""
    conn = obtener_conexion()
    try:
        yield conn
    finally:
        conn.close()


def obtener_dataframe(sql: str, chunksize: int = None):
    """Ejecuta una consulta SQL y devuelve un DataFrame o un generador si se solicita chunksize."""
    if not sql.strip():
        logging.getLogger(__name__).error("La consulta SQL no puede estar vacía.")
        raise ValueError("La consulta SQL no puede estar vacía.")

    logging.getLogger(__name__).info("Ejecutando consulta SQL en la base de datos...")
    with obtener_conexion() as conn:
        df = pd.read_sql_query(sql, conn, chunksize=chunksize)
    return df
