from utils.loader import dp
import logging
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import SYSTEM_PROMPT
from utils.database import get_connection

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        user_id = message.from_user.id
        full_name = message.from_user.full_name
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (id, full_name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            (user_id, full_name)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        await message.answer(f"Привет, {full_name}! {SYSTEM_PROMPT}. Задавай вопросы!")
    except Exception as e:
        logging.error(f"Error in /start: {e}")

@dp.message(Command("reset_context"))
async def reset_context_handler(message: Message):
    try:
        user_id = message.from_user.id
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM messages WHERE user_id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        await message.answer("Контекст диалога сброшен!")
    except Exception as e:
        logging.error(f"Error in /reset_context: {e}")