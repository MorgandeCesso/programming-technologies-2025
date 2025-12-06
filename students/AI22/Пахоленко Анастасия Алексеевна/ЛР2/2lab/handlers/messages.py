from utils.loader import dp
import logging
from aiogram.types import Message
from aiogram import F
from utils.gpt import get_response_with_context
from utils.database import db


@dp.message(F.text)
async def message_handler(message: Message) -> None:
    try:
        user_id = message.from_user.id
        user_name = message.from_user.first_name or message.from_user.username or "пользователь"
        
        
        db.add_user(
            user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        
        response = await get_response_with_context(message.text, user_id, user_name)
        await message.answer(response)
        
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при получении ответа")