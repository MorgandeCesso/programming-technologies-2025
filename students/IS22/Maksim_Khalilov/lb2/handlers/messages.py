from utils.loader import dp
import logging
from aiogram.types import Message
from utils.gpt import get_response, client
from utils.database import add_message
from aiogram import F

@dp.message()
async def message_handler(message: Message) -> None:
    try:
        if message.text:
            response = await get_response(message.text, message.from_user.id, message.from_user.full_name, client)
            await message.answer(response)
        elif message.photo:
            await message.answer("Я не работаю с изображениями")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при получении ответа")