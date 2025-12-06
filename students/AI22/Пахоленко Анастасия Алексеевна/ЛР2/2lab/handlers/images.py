from utils.loader import dp
import logging
from aiogram.types import Message
from aiogram import F
from aiogram.enums import ContentType


@dp.message(F.content_type == ContentType.PHOTO)
async def photo_handler(message: Message) -> None:
    try:
        
        photo = message.photo[-1]  
        file_id = photo.file_id
        
        
        logging.info(f"User {message.from_user.id} sent photo with file_id: {file_id}")
        
        
        await message.answer(
            "Вы отправили картинку!\n\n"
            "К сожалению, я пока не умею анализировать изображения, "
            "но я хорошо понимаю текст! Напишите мне что-нибудь, и я с радостью помогу!"
        )
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при обработке изображения")

@dp.message(F.content_type == ContentType.DOCUMENT)
async def document_handler(message: Message) -> None:
    try:
        await message.answer(
            "Вы отправили документ!\n\n"
            "В настоящее время я работаю только с текстовыми сообщениями. "
            "Напишите мне текстом, и я с радостью помогу!"
        )
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при обработке документа")

@dp.message(F.content_type == ContentType.VIDEO)
async def video_handler(message: Message) -> None:
    try:
        await message.answer(
            "Вы отправили видео!\n\n"
            "В настоящее время я работаю только с текстовыми сообщениями. "
            "Напишите мне текстом, и я с радостью помогу!"
        )
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при обработке видео")

@dp.message(F.content_type == ContentType.AUDIO)
async def audio_handler(message: Message) -> None:
    try:
        await message.answer(
            "Вы отправили аудио!\n\n"
            "В настоящее время я работаю только с текстовыми сообщениями. "
            "Напишите мне текстом, и я с радостью помогу!"
        )
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при обработке аудио")


@dp.message(F.content_type == ContentType.VOICE)
async def voice_handler(message: Message) -> None:
    try:
        await message.answer(
            "Вы отправили голосовое сообщение!\n\n"
            "В настоящее время я работаю только с текстовыми сообщениями. "
            "Напишите мне текстом, и я с радостью помогу!"
        )
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при обработке голосового сообщения")