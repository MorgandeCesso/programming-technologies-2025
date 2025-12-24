# Лабораторная работа №2. Тема: Простейший чат-бот в Telegram

<ins>Цель</ins>: получение навыков работы с библиотекой Aiogram, связка API OpenAI и написанного бота.

## План

1. Настройка окружения;
2. Написание основных функций бота;
3. Задания.

---

## _1. Настройка окружения_

Следуя инструкции, в BotFather был создан бот с именем Laba3 и адресом @SureItNoSensebot. Создана команда /start и файл .env с токеном бота. Также было создано виртуальное окружение, установлены нужные библитеки и скопированы в файл requirements.txt.

## _2. Написание основных функций бота_

Написание основных функций происходило по исторукции, но с некоторыми изменениями. Для работы бота, как и в предыдущей лабораторной работе, использовался Mistral AI. Ниже представлены изменённые файлы:

- Файл config.py:

```python
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
TEMPERATURE = os.getenv("TEMPERATURE")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
```

- Файл gpt.py, сделан по аналогии с прошлой лабораторной работой:

```python
from mistralai import Mistral
from config import MISTRAL_API_KEY, SYSTEM_PROMPT, TEMPERATURE

client = Mistral(api_key=MISTRAL_API_KEY)
```

- Немного изменён файл commands.py, здесь инициированы две команды бота:

```python
from utils.loader import dp
import logging
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from config import SYSTEM_PROMPT
from utils.database import get_connection

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        user_id = message.from_user.id
        full_name = message.from_user.full_name
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (id, full_name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            (user_id, full_name)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        await message.answer(f"Привет, {full_name}! {SYSTEM_PROMPT}. Задавай вопросы!")
    except Exception as e:
        logging.error(f"Error in /start: {e}")

@dp.message(Command("reset_context"))
async def reset_context_handler(message: Message):
    try:
        user_id = message.from_user.id
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM messages WHERE user_id = %s", (user_id,))
        conn.commit()
        cur.close()
        conn.close()
        await message.answer("Контекст диалога сброшен!")
    except Exception as e:
        logging.error(f"Error in /reset_context: {e}")
```

- В файле messages.py прописана логика взаимодействия с базой данных:

```python
from utils.loader import dp
import logging
from aiogram.types import Message, ContentType
from utils.mistral import client, SYSTEM_PROMPT, TEMPERATURE
from utils.database import get_connection

@dp.message()
async def message_handler(message: Message):
    try:
        user_id = message.from_user.id
        
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO users (id, full_name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING",
            (user_id, message.from_user.full_name)
        )
        
        cur.execute(
            "INSERT INTO messages (user_id, content, role) VALUES (%s, %s, %s)",
            (user_id, message.text, 'user')
        )
        
        cur.execute(
            """
            SELECT role, content 
            FROM messages 
            WHERE user_id = %s 
            ORDER BY id DESC 
            LIMIT 10
            """,
            (user_id,)
        )
        
        history = cur.fetchall()
        history.reverse()
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        for role, content in history:
            messages.append({"role": role, "content": content})
        
        messages.append({"role": "user", "content": message.text})
        
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=messages,
            temperature=TEMPERATURE
        )
        
        response_text = response.choices[0].message.content
        
        cur.execute(
            "INSERT INTO messages (user_id, content, role) VALUES (%s, %s, %s)",
            (user_id, response_text, 'assistant')
        )
        
        conn.commit()
        cur.close()
        conn.close()
        
        await message.answer(response_text)
        
    except Exception as e:
        logging.error(f"Error in message handler: {e}")
        await message.answer("Произошла ошибка при обработке сообщения")
```

- Был добавлен файл databaase.py с подключением к базе данных. Использовал pgadmin4 с postrgress
- 
```python
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

def get_connection():
    return psycopg2.connect(
        dbname="telegram_bot_db",
        user="postgres",
        password="qwas12",
        host="localhost",
        port="5432"
    )
```
Все остальные лабораторные без изменений

![Рисунок 1](pictures/1.png)

_Рисунок 1: Запуск файла main.py_

![Рисунок 2](pictures/2.png)

_Рисунок 2: Работа чат-бота в Telegram_

## _3. Задания_

1. В первом задании нужно было добавить ассистенту системный промпт. По аналогии с прошлой лабораторной работой, были изменены файл config.py и gpt.py, системный промпт берётся из переменного окружения .env:

```python
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
```

```python
import aiohttp
import logging
from config import SYSTEM_PROMPT

def create_prompt(system_prompt: str, user_input: str) -> str:
    return f"{system_prompt}\n\nПользователь: {user_input}\nАссистент:"

async def get_response(text: str) -> str:
    try:
        full_prompt = create_prompt(SYSTEM_PROMPT, text)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen3:4b",
                    "prompt": full_prompt,
                    "stream": False
                }
            ) as response:
                data = await response.json()
                return data["response"]

    except Exception as e:
        logging.error(f"Error: {e}")
        return "Ошибка при обращении к локальной модели"
```

Также был добавлен вывод системного промпта в чат для пользователя. Для этого файл commands.py был изменён:

```python
from utils.loader import dp
import logging
from aiogram.filters import CommandStart
from aiogram.types import Message
from config import SYSTEM_PROMPT

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    try:
        await message.answer(f"Привет, {message.from_user.full_name}, я твой бот-ассистент! Можешь задавать мне вопросы, и я буду отвечать на них.")
        await message.answer(f"Сейчас задействован системный промпт:\n{SYSTEM_PROMPT}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
```

Работа чат-бота с системным промптом (рис. 3):

![Рисунок 3](pictures/3.png)

_Рисунок 3: Чат-бот с системным промптом_

2. В данном задании нужно было сделать так, чтобы бот знал имя пользователя и при ответе обращался к нему по имени. В примере из лабораторной реализовано обращение к пользователю при запуске чат-бота. Теперь сделаем так, чтобы чат-бот при каждом ответе добавлял в начало имя пользователя. Был изменён файл messages.py:

```python
from utils.loader import dp
import logging
from aiogram.types import Message
from utils.gpt import get_response

@dp.message()
async def message_handler(message: Message) -> None:
    try:
        response = await get_response(message.text)
        name = message.from_user.first_name
        await message.answer(f"{name}, {response}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при получении ответа от модели")
```

Теперь при ответе, чат-бот обращается к пользователю по имени (рис. 4):

![Рисунок 4](pictures/4.png)

_Рисунок 4: Обращение по имени к пользователю при ответе_

3. В третьем задании нужно было добавить базу данных, для хранения сообщений. Для этого была создана база данных SQLite с использованием асинхронного ORM SQLAlchemy. В файле database.py было реализовано подключение к базе и описана таблица messages для хранения id, пользовательский id, имя пользователя, его сообщение, ответ чат-бота и время отправки:

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone
import asyncio

engine = create_async_engine('sqlite+aiosqlite:///messages.db', echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    username = Column(String)
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_message(user_id: int, username: str, message: str, response: str):
    async with async_session() as session:
        async with session.begin():
            new_message = Message(
                user_id=user_id,
                username=username,
                message=message,
                response=response
            )
            session.add(new_message)
```

Также был изменён файл messages.py, в который была добавлена логика сохранения сообщений в базу данных:

```python
from utils.loader import dp
import logging
from aiogram.types import Message, ContentType
from utils.gpt import get_response
from utils.database import save_message

@dp.message()
async def message_handler(message: Message) -> None:
    try:

        user_id = message.from_user.id
        username = message.from_user.first_name
        text = message.text

        response = await get_response(user_id, username, text)

        await save_message(user_id, username, text, response)

        await message.answer(f"Вот ваш ответ на вопрос, {username}. {response}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при получении ответа от модели")
```

Ниже представле диалог с чат-ботом и вывод сохранённых сообщений (рис. 5, 6):

![Рисунок 5](pictures/5.png)

_Рисунок 5: Диалог с чат-ботом Telegram_

![Рисунок 6](pictures/6.png)

_Рисунок 6: Сохранённые сообщения в базе_

4. Теперь нужно было добавить поддержку контекста диалога, используя уже созданную базу данных. Для этого добавляем в файл database.py функцию get_history, которая берёт историю сообщений из базы данных messages.db:

```python
async def get_history(user_id: int, limit: int = 3):
    last_reset = await get_last_reset(user_id)
    async with async_session() as session:
        stmt = select(Message.message, Message.response).where(Message.user_id == user_id)

        if last_reset:
            stmt = stmt.where(Message.timestamp > last_reset)

        stmt = stmt.order_by(Message.id.desc()).limit(limit)
        result = await session.execute(stmt)
        rows = result.fetchall()

        return rows[::-1]
```

Далее меняем файл gpt.py по аналогии с прошлой лабораторной работой, чтобы функция get_response учитывала историю диалога, которая хранится в базе:

```python
async def get_response(user_id: int, username: str, user_message: str) -> str:
    try:
        history = await get_history(user_id)

        prompt = SYSTEM_PROMPT + "\n\nИстория диалога:\n"

        for msg, resp in history:
            prompt += f"Пользователь: {msg}\n"
            prompt += f"Ассистент: {resp}\n"

        prompt += f"\nПользователь: {user_message}\nАссистент:"
```

Также в файле messages.py теперь передаём в функцию get_response данные пользователя, чтобы формировать ответ с учётом истории диалога из базы данных:

```python
@dp.message()
async def message_handler(message: Message) -> None:
    try:
        user_id = message.from_user.id
        username = message.from_user.first_name
        text = message.text

        response = await get_response(user_id, username, text)

        await save_message(user_id, username, text, response)

        await message.answer(f"Вот ваш ответ на вопрос, {username}. {response}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при получении ответа от модели")
```

Ниже представле диалог с чат-ботом с учётом истории диалога (рис. 7):

![Рисунок 7](pictures/7.png)

_Рисунок 7: Диалог с чат-ботом Telegram с учётом истории диалога_

5. В данном задании нужно было добавить команду /reset-context для сброса контекста диалога. Чтобы не удалять ранее сохранённый в базе диалог, было решено фиксировать время последнего сброса в новой таблице и использовать только те сообщения в истории диалога, которые были отправлены после сброса. Для этого добавляем в файл database.py таблицу для хранения времени последнего сброса, также добавляем функции для получения времени последнего сброса и его обновления. Также в функции get_history теперь учитывается сброс контекста:

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, select, func
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime, timezone
import asyncio

engine = create_async_engine('sqlite+aiosqlite:///messages.db', echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    username = Column(String)
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class Session(Base):
    __tablename__ = 'session'

    user_id = Column(Integer, primary_key=True)
    last_reset = Column(DateTime)

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def save_message(user_id: int, username: str, message: str, response: str):
    async with async_session() as session:
        async with session.begin():
            new_message = Message(
                user_id=user_id,
                username=username,
                message=message,
                response=response
            )
            session.add(new_message)

async def get_last_reset(user_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(Session.last_reset).where(Session.user_id == user_id)
        )
        row = result.first()
        return row[0] if row else None

async def update_reset(user_id: int):
    async with async_session() as session:
        async with session.begin():
            existing = await session.get(Session, user_id)

            if existing:
                existing.last_reset = func.now()
            else:
                session.add(Session(user_id=user_id, last_reset=func.now()))

async def get_history(user_id: int, limit: int = 3):
    last_reset = await get_last_reset(user_id)
    async with async_session() as session:
        stmt = select(Message.message, Message.response).where(Message.user_id == user_id)

        if last_reset:
            stmt = stmt.where(Message.timestamp > last_reset)

        stmt = stmt.order_by(Message.id.desc()).limit(limit)
        result = await session.execute(stmt)
        rows = result.fetchall()

        return rows[::-1]
```

В файл commands.py была добавлена команда reset_context:

```python
@dp.message(Command("reset_context"))
async def reset_context_handler(message: Message):
    user_id = message.from_user.id

    await update_reset(user_id)

    await message.answer("Контекст диалога сброшен! Начинаем диалог заново.")
```

Вот пример диалога с чат-ботом с использованием команды /reset_context (рис. 8):

![Рисунок 8](pictures/8.png)

_Рисунок 8: Диалог с чат-ботом Telegram с использованием команды /reset_context_

Как видно на скриншоте, чат-бот учитывает контекст до использования команды /reset_context. После он не понимает кто такая "её" и отвечает, не учитывая сохранённый диалог.

6. В последнем задании нужно было добавить поддержку данных изображений, просто отправит на сообщение с изображением текст "Вы отправили картинку!". Для этого в файл messages.py был добавлен импорт ContentType, который позволяет определять тип входящего сообщения и обрабатывать сообщения с изображениями отдельно от текстовых. Также был добавлен обработчик для проверки является ли сообщение картинкой. Если да, то отправляем нужное сообщение и не обрабатываем его, если нет, то обрабатываем сообщение как всегда:

```python
from utils.loader import dp
import logging
from aiogram.types import Message, ContentType
from utils.gpt import get_response
from utils.database import save_message

@dp.message()
async def message_handler(message: Message) -> None:
    try:
        if message.content_type == ContentType.PHOTO:
            await message.answer("Вы отправили картинку!")
            return

        user_id = message.from_user.id
        username = message.from_user.first_name
        text = message.text

        response = await get_response(user_id, username, text)

        await save_message(user_id, username, text, response)

        await message.answer(f"Вот ваш ответ на вопрос, {username}. {response}")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при получении ответа от модели")
```

Ниже прадставлен диалог с чат-ботом и отправка ему картинки (рис. 9):

![Рисунок 9](pictures/9.png)

_Рисунок 9: Отправка картинки чат-боту Telegram_

Вывод: В ходе выполнения лабораторной работы был успешно реализован простейший чат-бот в Telegram с помощью локальной модели Ollama, библиотеки Aiogram и асинхронного ORM SQLAlchemy. Были выполнены все задания, а именно: добавлена системная подсказка по аналогии с прошлой лабораторной работой, добавлено обращение к пользователю по имени при ответе, добавлено хранение сообщений в базе данных SQLite messages.db с использованием ORM SQLAlchemy, добавлена поддержка контекста диалога, с использованием ранее созданной базы. Также добавлена команда /reset_context, позволяющая, не стирая сохранённую историю, сбросить контекст диалога. И добавлена обработка отправленных картинок с выводом сообщения «Вы отправили картинку!». Все функции чат-бота корректны и работоспособны. Таким образом лабораторная позволила получить навыки создания чат-бота в Telegram, работы с асинхронными ORM, добавления и редактирования команд для чат-бота, сохранять информацию о пользователе и сообщениях в чате в базе данных и также обрабатывать изображения.
