import asyncio
import logging
import sys
from handlers import dp
from utils.loader import bot
from utils.database import db  

async def main():
    try:
        print("=" * 50)
        print("Бот запущен и готов к работе!")
        print("=" * 50)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    asyncio.run(main())