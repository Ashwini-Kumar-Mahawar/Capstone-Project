# src/tools/persistence.py
import sqlite3
import json
from typing import Dict, Any

DB_PATH = "memory.db"

def init_db(path: str = DB_PATH):
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        user_id TEXT PRIMARY KEY,
        data TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    return conn

def save_memory(conn: sqlite3.Connection, user_id: str, memory: Dict[str, Any]):
    data = json.dumps(memory, ensure_ascii=False)
    conn.execute(
        "INSERT INTO memory(user_id, data) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET data=excluded.data, updated_at=CURRENT_TIMESTAMP",
        (user_id, data)
    )
    conn.commit()

def load_memory(conn: sqlite3.Connection, user_id: str) -> Dict[str, Any]:
    cur = conn.execute("SELECT data FROM memory WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        return {}
    return json.loads(row[0])

def delete_memory(conn: sqlite3.Connection, user_id: str):
    conn.execute("DELETE FROM memory WHERE user_id=?", (user_id,))
    conn.commit()
