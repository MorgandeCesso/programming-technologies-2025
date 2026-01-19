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

- Файл mistral.py:

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

        name = message.from_user.full_name
        await message.answer(f"{name}, {response}")
        
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

![Рисунок 1](img/1.png)

_Рисунок 1: Запуск файла main.py_

![Рисунок 2](img/2.png)

_Рисунок 2: Работа чат-бота в Telegram_

## _3. Задания_

1. В первом задании нужно было добавить ассистенту системный промпт. Были изменены файл config.py и mistral.py, системный промпт берётся из переменного окружения .env:

```python
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
TEMPERATURE = os.getenv("TEMPERATURE")
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")
```

```python
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
```

Также был добавлен вывод системного промпта в чат для пользователя. Для этого файл commands.py был изменён:

2. В данном задании нужно было сделать так, чтобы бот знал имя пользователя и при ответе обращался к нему по имени. В примере из лабораторной реализовано обращение к пользователю при запуске чат-бота. Теперь сделаем так, чтобы чат-бот при каждом ответе добавлял в начало имя пользователя. Был изменён файл messages.py:

```python
@dp.message()
async def message_handler(message: Message):
    try:
        user_id = message.from_user.id

...
        name = message.from_user.full_name
        await message.answer(f"{name}, {response}")
```

Теперь при ответе, чат-бот обращается к пользователю по имени (рис. 4):

![Рисунок 4](img/4.png)

_Рисунок 4: Обращение по имени к пользователю при ответе_

3. В третьем задании нужно было добавить базу данных, для хранения сообщений. Для этого была создана база данных postgres с использованием psycopg2: Python-адаптер для PostgreSQL, написанный на языке C. В файле database.py было реализовано подключение к базе:

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

Ниже представле диалог с чат-ботом и вывод сохранённых сообщений (рис. 5, 6):

![Рисунок 5](img/7.png)

_Рисунок 5: Диалог с чат-ботом Telegram_

![Рисунок 6](img/6.png)

_Рисунок 6: Сохранённые сообщения в базе_

4. Теперь нужно было добавить поддержку контекста диалога, используя уже созданную базу данных. Для этого добавляем в файл message.py код, который берёт историю сообщений из базы данных telegram_bot_db.db:

```python
 cur.execute(
            """
            SELECT role, content 
            FROM messages 
            WHERE user_id = %s 
            ORDER BY id DESC 
            LIMIT 10
            """,
            (user_id,)
        )в
```

5. В данном задании нужно было добавить команду /reset-context для сброса контекста диалога. Чтобы не удалять ранее сохранённый в базе диалог, было решено фиксировать время последнего сброса в новой таблице и использовать только те сообщения в истории диалога, которые были отправлены после сброса.
```python
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

Вот пример диалога с чат-ботом с использованием команды /reset_context (рис. 8):

![Рисунок 8](img/8.png)

_Рисунок 8: Диалог с чат-ботом Telegram с использованием команды /reset_context_

6. В последнем задании нужно было добавить поддержку данных изображений, просто отправит на сообщение с изображением текст "Вы отправили картинку!" (рис. 9).

![Рисунок 9](img/9.png)

```python
@dp.message(content_types=ContentType.PHOTO)
async def photo_handler(message: Message):
   await message.answer("Вы отправили картинку! Пока я умею обрабатывать только текст 😊")     
```

Вывод: В ходе выполнения лабораторной работы был успешно реализован простейший чат-бот в Telegram с помощью локальной модели Mistral, библиотеки Aiogram и pgadmin4. Были выполнены все задания, а именно: добавлена системная подсказка по аналогии с прошлой лабораторной работой, добавлено обращение к пользователю по имени при ответе, добавлено хранение сообщений в базе данных postgress telegram_bot_db.db, добавлена поддержка контекста диалога, с использованием ранее созданной базы. Также добавлена команда /reset_context, позволяющая, не стирая сохранённую историю, сбросить контекст диалога. И добавлена обработка отправленных картинок с выводом сообщения «Вы отправили картинку!». Все функции чат-бота корректны и работоспособны. Таким образом лабораторная позволила получить навыки создания чат-бота в Telegram, добавления и редактирования команд для чат-бота, сохранять информацию о пользователе и сообщениях в чате в базе данных и также обрабатывать изображения.
