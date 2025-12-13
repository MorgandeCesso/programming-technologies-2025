import sqlite3

conn = sqlite3.connect("messages.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    message TEXT,
    response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS session (
    user_id INTEGER PRIMARY KEY,
    last_reset TIMESTAMP
)
""")

conn.commit()

def save_message(user_id: int, username: str, message: str, response: str):
    cursor.execute("""
        INSERT INTO messages (user_id, username, message, response)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, message, response))

    conn.commit()

def get_last_reset(user_id: int):
    cursor.execute("""
        SELECT last_reset FROM session WHERE user_id = ?
    """, (user_id,))
    
    row = cursor.fetchone()
    return row[0] if row else None

def update_reset(user_id: int):
    cursor.execute("""
        INSERT OR REPLACE INTO session (user_id, last_reset)
        VALUES (?, CURRENT_TIMESTAMP)
    """, (user_id,))
    conn.commit()

def get_history(user_id: int, limit: int = 3):
    last_reset = get_last_reset(user_id)

    if last_reset:
        cursor.execute("""
            SELECT message, response FROM messages
            WHERE user_id = ? AND timestamp > ?
            ORDER BY id DESC
            LIMIT ?
        """, (user_id, last_reset, limit))
    else:
        cursor.execute("""
            SELECT message, response FROM messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (user_id, limit))

    return cursor.fetchall()[::-1] 

