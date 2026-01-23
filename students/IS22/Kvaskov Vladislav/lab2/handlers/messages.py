from utils.loader import dp
import logging
from aiogram.types import Message
from utils.gpt import get_response, client
from aiogram.types import ContentType
from models import User, MessageDB

content_type_names = {
    ContentType.PHOTO: " с фото",
    ContentType.VIDEO: "с видео",
    ContentType.DOCUMENT: "с документами",
    ContentType.AUDIO: "с аудио",
    ContentType.VOICE: "с голосовыми сообщениями",
    ContentType.STICKER: "со стикерами",
    ContentType.ANIMATION: "с гифками",
    ContentType.CONTACT: "с контактами",
    ContentType.LOCATION: "с локациями",
}


@dp.message()
async def message_handler(message: Message) -> None:
    try:
        if message.text: 

            username = message.from_user.full_name
            id_user = message.from_user.id

            user, created = await User.get_or_create(user_id_db=id_user, defaults={'username_db': username})

            history = await MessageDB.filter(user_id=id_user, context_db=True).order_by('created_db')
            
            if not history:
                history = []

            response = await get_response(message.text,  username , client,  history)

            await MessageDB.create(message_db=message.text, response_db=response, user_id=user, context_db = True)

            await message.answer(response)
        else:
           content_type = content_type_names.get(message.content_type)
           await message.answer(f'Извини {message.from_user.full_name}, но я не работаю {content_type}')
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при получении ответа")