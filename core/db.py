# futbol_app/db.py
import os
import psycopg2

def get_connection():
    """
    Si existe DATABASE_URL (ej. Azure), la usa directamente.
    Si no, usa variables locales (host, puerto, etc.).
    """
    url = os.getenv("DATABASE_URL")
    if url:
        # Ejemplo: postgresql://USER:PASS@HOST:5432/DB?sslmode=require
        return psycopg2.connect(url)

    # ---- Modo local por variables ----
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "futbol_gestion")
    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "12345")
    sslmode = os.getenv("DB_SSLMODE", "disable")  # "require" para Azure

    dsn = f"host={host} port={port} dbname={dbname} user={user} password={password}"
    if sslmode and sslmode.lower() != "disable":
        dsn += f" sslmode={sslmode}"

    return psycopg2.connect(dsn)
