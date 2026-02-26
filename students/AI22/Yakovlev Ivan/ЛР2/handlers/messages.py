from utils.loader import dp
import logging
from aiogram.types import Message
from aiogram import F
from utils.gpt import get_response, client

@dp.message(F.photo)
async def handle_photo(message: Message):
    await message.answer("Вы отправили картинку!")

@dp.message(F.text)
async def message_handler(message: Message) -> None:
    try:
        response = await get_response(message.text, client, message.from_user.full_name, message.from_user.id)
        await message.answer(response)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при получении ответа")