from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT", "Ты полезный ассистент. Отвечай по делу.")

# Сколько последних сообщений брать в контекст (из БД)
CONTEXT_LIMIT = int(os.getenv("CONTEXT_LIMIT", "12"))

# SQLite файл
DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///bot.db")
