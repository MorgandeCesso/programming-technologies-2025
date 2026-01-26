from aiogram import Router
from aiogram.types import Message

from utils.gpt import get_response_with_context

router = Router()


@router.message()
async def chat_handler(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    response = await get_response_with_context(
        message=message.text,
        user_id=user_id,
        user_name=user_name
    )

    await message.answer(response)
