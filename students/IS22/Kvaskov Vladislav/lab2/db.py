import os
from tortoise import Tortoise
from urllib.parse import urlparse
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

url = urlparse(DATABASE_URL)

async def init_db():
    await Tortoise.init(
        db_url=f'postgres://{url.username}:{url.password}@{url.hostname}:{url.port}{url.path}',
        modules={'models': ['models']}  
    )
    await Tortoise.generate_schemas()


