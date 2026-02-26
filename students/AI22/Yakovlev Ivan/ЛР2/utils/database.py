import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'chat_history.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('CREATE INDEX IF NOT EXISTS idx_user_timestamp ON messages(user_id, timestamp DESC)')

def save_message(user_id: int, role: str, content: str):
    with get_db() as conn:
        conn.execute(
            'INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)',
            (user_id, role, content)
        )

def get_recent_messages(user_id: int, limit: int = 6):
    with get_db() as conn:
        cursor = conn.execute(
            'SELECT role, content FROM messages WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?',
            (user_id, limit)
        )
        rows = cursor.fetchall()
        # Возвращаем в хронологическом порядке (от старых к новым)
        return [{"role": row["role"], "content": row["content"]} for row in reversed(rows)]

def clear_context(user_id: int):
    with get_db() as conn:
        conn.execute('DELETE FROM messages WHERE user_id = ?', (user_id,))