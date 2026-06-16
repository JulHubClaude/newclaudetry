"""SQLite-Verbindung und Schema-Initialisierung."""
from __future__ import annotations

import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "transactions.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


def get_connection(db_path: Path | str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Öffnet eine SQLite-Verbindung mit Row-Factory für Dict-artigen Zugriff."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Legt Tabellen und Indizes an (idempotent)."""
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema_sql)
    conn.commit()


def reset_database(db_path: Path | str = DEFAULT_DB_PATH) -> None:
    """Löscht die DB-Datei und legt sie neu an. Nur für Tests/Re-Imports."""
    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()
    with get_connection(db_path) as conn:
        init_schema(conn)
