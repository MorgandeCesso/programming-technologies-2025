import sqlite3

conn = sqlite3.connect("messages.db")
cursor = conn.cursor()

# создаём таблицу, если её нет
cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    user_id INTEGER,
    role TEXT,
    content TEXT
)
""")
conn.commit()


def add_message(user_id: int, role: str, content: str):
    cursor.execute(
        "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
        (user_id, role, content)
    )
    conn.commit()


def get_messages(user_id: int, limit: int = 10):
    cursor.execute(
        "SELECT role, content FROM messages WHERE user_id = ? ORDER BY ROWID DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    return list(reversed(rows))  # чтобы шло в правильном порядке


def reset_messages(user_id: int):
    cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
    conn.commit()
