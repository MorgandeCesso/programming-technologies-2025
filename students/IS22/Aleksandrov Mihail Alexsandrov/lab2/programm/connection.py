from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine

DB_URL = f'postgresql+asyncpg://postgres:dwin45@localhost:5432/tgbot'
engine: AsyncEngine = create_async_engine(DB_URL, echo=True)
