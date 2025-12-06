import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class Database:
    def __init__(self, db_name: str = "chat_bot.db"):
        
        db_path = os.path.abspath(db_name)
        
        db_dir = os.path.dirname(db_path)
        if db_dir:  
            os.makedirs(db_dir, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
        print(f"База данных создана/подключена: {db_path}")
    
    def create_tables(self):
        cursor = self.conn.cursor()
        
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS context (
            user_id INTEGER PRIMARY KEY,
            messages TEXT, -- JSON список сообщений
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')
        
        self.conn.commit()
        print("Таблицы созданы/проверены")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name))
        self.conn.commit()
    
    def save_message(self, user_id: int, role: str, content: str):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO messages (user_id, role, content)
        VALUES (?, ?, ?)
        ''', (user_id, role, content))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_user_messages(self, user_id: int, limit: int = 10) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT role, content, timestamp 
        FROM messages 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
        ''', (user_id, limit))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'role': row[0],
                'content': row[1],
                'timestamp': row[2]
            })
        return messages[::-1] 
    
    def save_context(self, user_id: int, messages: List[Dict]):
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO context (user_id, messages, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, json.dumps(messages, ensure_ascii=False)))
        self.conn.commit()
    
    def get_context(self, user_id: int) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT messages FROM context WHERE user_id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result and result[0]:
            return json.loads(result[0])
        return []
    
    def clear_context(self, user_id: int):
        cursor = self.conn.cursor()
        cursor.execute('''
        DELETE FROM context WHERE user_id = ?
        ''', (user_id,))
        self.conn.commit()
    
    def close(self):
        self.conn.close()
        print("Соединение с базой данных закрыто")


db = Database()