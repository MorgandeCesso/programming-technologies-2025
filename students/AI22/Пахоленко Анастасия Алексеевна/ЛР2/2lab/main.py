import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import TOKEN
from db.base import engine, Base

from handlers.commands import router as commands_router
from handlers.images import router as images_router
from handlers.messages import router as messages_router


logging.basicConfig(level=logging.INFO)


async def main():
    
    Base.metadata.create_all(bind=engine)

    
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    
    await bot.set_my_commands([
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="prompt", description="Задать системный промпт"),
        BotCommand(command="reset", description="Сбросить контекст диалога"),
    ])

    
    dp.include_router(commands_router)
    dp.include_router(images_router)
    dp.include_router(messages_router)

    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
