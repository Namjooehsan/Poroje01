import os
import sqlite3
from datetime import datetime, timezone

DB_PATH = os.getenv("DATABASE_PATH", "recoverybot.sqlite3")


def connect():
    folder = os.path.dirname(DB_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                note TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS device_status (
                device_id TEXT PRIMARY KEY,
                android_version TEXT,
                python_version TEXT,
                adb_status TEXT,
                last_seen TEXT NOT NULL
            )
        """)


def add_note(user_id: int, note: str):
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute(
            "INSERT INTO notes (telegram_user_id, note, created_at) VALUES (?, ?, ?)",
            (user_id, note[:500], now),
        )


def get_notes(user_id: int, limit: int = 10):
    with connect() as conn:
        rows = conn.execute(
            "SELECT note, created_at FROM notes WHERE telegram_user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return rows


def update_device(device_id: str, android_version: str, python_version: str, adb_status: str):
    now = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        conn.execute("""
            INSERT INTO device_status(device_id, android_version, python_version, adb_status, last_seen)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(device_id) DO UPDATE SET
                android_version=excluded.android_version,
                python_version=excluded.python_version,
                adb_status=excluded.adb_status,
                last_seen=excluded.last_seen
        """, (device_id[:80], android_version[:40], python_version[:40], adb_status[:40], now))


def get_device(device_id: str = "huawei-android"):
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM device_status WHERE device_id=?", (device_id,)
        ).fetchone()
