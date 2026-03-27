from utils.loader import dp
import logging
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import SYSTEM_PROMPT
from utils.db import save_history, get_history

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        await message.answer(f"Привет, {message.from_user.full_name}, я - бот-ассистент! Можешь задавать мне вопросы, и я буду отвечать на них.")
        await message.answer(f"Системный промт в настоящий момент:\n{SYSTEM_PROMPT}") 
    except Exception as e:
        logging.error(f"Error occurred: {e}")

@dp.message(Command("clear"))
async def reset_context(message: Message):
    user_id = message.from_user.id  # Получаем user_id из сообщения

    # Получаем историю диалога из базы данных
    dialog_history_actual = get_history(user_id)

    if dialog_history_actual:  # Если история найдена, сбрасываем её
        dialog_history_actual = []  # Очищаем историю для данного пользователя
        save_history(user_id, dialog_history_actual)  # Сохраняем пустую историю в БД
        await message.answer("Контекст диалога успешно сброшен")
    else:
        await message.answer("Ошибка: история дилога не найдена")
