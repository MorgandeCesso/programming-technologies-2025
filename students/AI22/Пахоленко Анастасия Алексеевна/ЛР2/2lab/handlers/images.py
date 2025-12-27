from aiogram import Router
from aiogram.types import Message

router = Router()


@router.message(lambda message: message.photo)
async def photo_handler(message: Message):
    await message.answer("Вы отправили картинку!")
