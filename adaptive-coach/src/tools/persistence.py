# src/tools/persistence.py

import sqlite3
import json
from typing import Dict, Any
from rich.console import Console

# Rich console (Windows-safe)
console = Console(soft_wrap=True, force_jupyter=False)

DB_PATH = "memory.db"


def sanitize(msg: str) -> str:
    """
    Removes Unicode characters Windows CMD cannot encode.
    Converts common symbols (✔ → [OK]) and strips others.
    """
    replacements = {
        "✔": "[OK]",
        "✘": "[X]",
        "✓": "[OK]"
    }
    
    for bad, good in replacements.items():
        msg = msg.replace(bad, good)
    
    # Remove unencodable chars
    return msg.encode("ascii", "ignore").decode()


def log(msg: str, style: str = "green"):
    """
    Safe logger for Windows terminals.
    Prevents UnicodeEncodeError and Rich markup issues.
    """
    msg = sanitize(msg)
    console.print(f"[{style}]{msg}[/]", markup=False)


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

    log("[OK] SQLite memory database initialized.", "green")
    return conn


def save_memory(conn: sqlite3.Connection, user_id: str, memory: Dict[str, Any]):
    data = json.dumps(memory, ensure_ascii=False)
    conn.execute(
        """
        INSERT INTO memory(user_id, data)
        VALUES (?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET data=excluded.data, updated_at=CURRENT_TIMESTAMP
        """,
        (user_id, data)
    )
    conn.commit()
    log(f"[OK] Memory saved for {user_id}", "cyan")


def load_memory(conn: sqlite3.Connection, user_id: str) -> Dict[str, Any]:
    cur = conn.execute("SELECT data FROM memory WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    if not row:
        log(f"[OK] No memory found for {user_id}. Returning empty object.", "yellow")
        return {}

    log(f"[OK] Memory loaded for {user_id}", "cyan")
    return json.loads(row[0])


def delete_memory(conn: sqlite3.Connection, user_id: str):
    conn.execute("DELETE FROM memory WHERE user_id=?", (user_id,))
    conn.commit()
    log(f"[OK] Memory deleted for {user_id}", "red")
