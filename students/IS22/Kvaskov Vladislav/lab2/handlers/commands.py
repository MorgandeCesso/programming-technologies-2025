from utils.loader import dp
import logging
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import logging
from models import MessageDB

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        await message.answer(f"Привет, {message.from_user.full_name}, я твой бот-ассистент! Можешь задавать мне вопросы")
    except Exception as e:
        logging.error(f"Error occurred: {e}")

@dp.message(Command("reset_context"))
async def reset_context(message: Message) -> None:
    try:
        user_id = message.from_user.id
        
        reset_messages = await MessageDB.filter(user_id=user_id, context_db=True)

        if reset_messages:
            await MessageDB.filter(user_id=user_id, context_db=True).update(context_db=False)
            await message.answer("Контекст диалога был сброшен.")
        else:
            await message.answer("Контекст диалога нельзя сбросить. Пожалуйста, пообщайтесь с ассисентом, прежде чем сбросить контекст.")
        
    except Exception as e:
        logging.error(f"Error occurred while resetting context: {e}")
        await message.answer("Произошла ошибка при сбросе контекста.")
    