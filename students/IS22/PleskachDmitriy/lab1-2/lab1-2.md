Министерство науки и высшего образования РФ ФГБОУ ВО

Заполярный государственный институт имени Н.М.Федоровского






Технологии программирования.

Лабораторная работа №2

Тема: «Простейший чат-бот в Telegram»




Работу выполнил:

Студент группы ИС – 22\
Плескач Дмитрий

Работу проверил:

Сидельников Максим Эдуардович



Норильск, 2025

\
**Цель работы**

Цель лабораторной работы — получение навыков работы с библиотекой Aiogram, связка API OpenAI и написанного бота.

Инструменты и настройки:

- Язык программирования: Python.
- Библиотеки:

  openai — для работы с API.

  dotenv — для загрузки переменных окружения (например, API-ключ).

  aiogram - для работы с Telegram API, предоставляет удобный асинхронный интерфейс для создания ботов, обработки сообщений, команд и взаимодействия с пользователем.

В коде были реализованы следующие задачи:

1\.Добавление к ассистенту системный промпт:

```python
from config import OPENAI_API_KEY, SYSTEM_PROMPT, TEMPERATURE

async def get_response(
    message: str, username: str, context_data: str, client: AsyncOpenAI) -> str:
    try:
        personalized_prompt = (
            SYSTEM_PROMPT.format(username=username)
            if "{username}" in SYSTEM_PROMPT
            else f"{SYSTEM_PROMPT} Общайся с пользователем по имени {username}."
        )
        response = await client.responses.create(
            model="gpt-4.1-nano",
            input=message,
            instructions=personalized_prompt,
            temperature=TEMPERATURE,
        )
        return response.output_text
```
Переменная SYSTEM\_PROMPT= «Ты маэстро музыки, разбираешься во всех тонкостях музыки и чинишь гитары. Веди себя надменно как будто ты все знаешь и для тебя все очевидно.»

Результат работы:

Бот генерирует ответы, используя системный контекст.

\
![](assets/1.png)

\
Добавление функции обращения к пользователю по имени: Для того чтобы бот знал имя пользователя, используем атрибут message.from\_user.full\_name
```python
@dp.message(CommandStart())

async def start(message: Message):

    await message.answer(
        f"Привет, {message.from\_user.full\_name}! Я бот-ассистент.")

@dp.message(Command("reset_context"))

async def reset_context(message: Message):
    db.clear(message.from_user.id)
    await message.answer("Контекст диалога сброшен.")и передаем в функцию запроса к ChatGPT через системный промт

async def get_response(
    message: str, username: str, context_data: str, client: AsyncOpenAI) -> str:
    try:

        personalized_prompt = (
            SYSTEM_PROMPT.format(username=username)
            if "{username}" in SYSTEM_PROMPT
            else f"{SYSTEM_PROMPT} Общайся с пользователем по имени {username}.")

        response = await client.responses.create(
            model="gpt-4.1-nano",
            input=full_message,
            instructions=personalized_prompt,
            temperature=TEMPERATURE,)

        return response.output_text
```
Добавление хранения истории сообщений и поддержку контекста диалога:
```python
class Message(Base):

    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String)
    user_message = Column(Text)
    assistant_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    in_history = Column(Boolean, default=True)

class DatabaseManager:
    def get_last_messages(self, user_id: int, limit: int = 5) -> list[dict]:
       session = self.SessionLocal()
        try:
            msgs = (
                session.query(Message)
.filter(Message.user_id == user_id, Message.in_history == True)
.order_by(Message.create_at.desc())
.limit(limit)
.all())
            msgs = list(reversed(msgs))
            result = []
            for msg in msgs:
                result.append(
                    {
                        "user_message": msg.user_message,
                        "assistant_message": msg.assistant_message,
                    }
                 )
            return result
        finally:
session.close()
```
Для того, чтобы ИИ помнил контекст общения с пользователем, была реализована система ведения истории диалога. История ограницивается 10 последними сообщениями. У каждого пользователя свой сохраненный контекст.

Для упрощения задачи и быстрого прототипирования я решил использовать файл SQLite для хранения истории сообщений и подключаться к нему, что позволяет эффективно управлять данными без необходимости использования более сложных баз данных. Это обеспечило простоту реализации и ускорение процесса разработки, что идеально подходит для учебного прототипа.

Добавление команды /resetcontext, которая будет сбрасывать контекст диалога
```python
@dp.message(Command("reset_context"))

async def command_reset_context_handler(message: Message) -> None:
    `try:
        user_id = message.from_user.id
        db_manager.clear_history(user_id)
        file_path = f"data_json/history_{user_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        await message.answer("Контекст диалога успешно сброшен.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при сбросе контекста диалога.")

def clear_history(self, user_id: int) -> int:
    session = self.SessionLocal()
    try:
        updated_count = (
            `session.query(Message)
.filter(Message.user_id == user_id, Message.in_history == True)
.update({"in_history": False}))
        session.commit()
        return updated_count
    finally:
        session.close()
```
Для реализации команды /reset\_context, которая сбрасывает контекст диалога, я создал обработчик для этой команды, который проверяет, есть ли сохраненная история для конкретного пользователя, используя его уникальный user\_id. Когда пользователь отправляет команду /resetcontext, я извлекаю его user\_id из сообщения с помощью message.from\_user.id. Затем, проверяя, существует ли история диалога этого user\_id в таблице, я меняю флаг у сообщений, чтобы они больше не использовались в истории и также отчищаю JSON, который хранит историю в рамках одной сессии. После этого отправляется сообщение, подтверждающее, что история была сброшена и можно начать новый разговор.

![](assets/2.png)
\
![](assets/3.png)\
\
Добавление хранения истории сообщений и поддержку контекста диалога:
```python
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    username = Column(String)
    user_message = Column(Text)
    assistant_message = Column(Text)
    created_at = Column(DateTime, default=func.now())
    in_history = Column(Boolean, default=True)

class DatabaseManager:
    def get_last_messages(self, user_id: int, limit: int = 5) -> list[dict]:
        session = self.SessionLocal()
        try:
            msgs = (
                session.query(Message)
.filter(Message.user_id == user_id, Message.in_history == True)
.order_by(Message.created_at.desc())
.limit(limit)
.all())
            msgs = list(reversed(msgs))
            result = []
            for msg in msgs:
                result.append(
                    {
                        "user_message": msg.user_message,
                        "assistant_message": msg.assistant_message,
                    }
                )
            return result
        finally:
            session.close()
```
Для того, чтобы ИИ помнил контекст общения с пользователем, была реализована система ведения истории диалога. История ограницивается 10 последними сообщениями. У каждого пользователя свой сохраненный контекст.

Для упрощения задачи и быстрого прототипирования я решил использовать файл SQLite для хранения истории сообщений и подключаться к нему, что позволяет эффективно управлять данными без необходимости использования более сложных баз данных. Это обеспечило простоту реализации и ускорение процесса разработки, что идеально подходит для учебного прототипа.

Добавление команды /reset\_context, которая будет сбрасывать контекст диалога
```python
@dp.message(Command("reset_context"))

async def command_reset_context_handler(message: Message) -> None:
    try:
        user_id = message.from_user.id
        db_manager.clear_history(user_id)
        file_path = f"data_json/history_{user_id}.json"
        if os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        await message.answer("Контекст диалога успешно сброшен.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        await message.answer("Произошла ошибка при сбросе контекста диалога.")
def clear_history(self, user_id: int) -> int:
    session = self.SessionLocal()
    try:
        updated_count = (
            session.query(Message)
.filter(Message.user_id == user_id, Message.in_history == True)
.update({"in_history": False}))

        session.commit()
        return updated_count
    finally:
`        session.close()
```
Для реализации команды /reset\_context, которая сбрасывает контекст диалога, я создал обработчик для этой команды, который проверяет, есть ли сохраненная история для конкретного пользователя, используя его уникальный user\_id. Когда пользователь отправляет команду /resetcontext, я извлекаю его user\_id из сообщения с помощью message.from\_user.id. Затем, проверяя, существует ли история диалога этого user\_id в таблице, я меняю флаг у сообщений, чтобы они больше не использовались в истории и также отчищаю JSON, который хранит историю в рамках одной сессии. После этого отправляется сообщение, подтверждающее, что история была сброшена и можно начать новый разговор.



![](assets/4.png)
![](assets/5.png)\
\
Добавление поддержки отправки изображений (без их обработки нейронкой).
```python
@dp.message()

async def message_handler(message: Message) -> None:
    try:
        if message.photo:
            await message.answer(
                "Вы отправили картинку! К сожалению, я не могу обрабатывать изображения.")
            Return
```
Для обработки сообщений, отличных от текста (например, изображений, видео и других медиа), я добавил проверку типа сообщения с помощью message.photo,которое проверяет, является ли отперавленое сообщение фотографией. Если да, то вывожу пользователю сообщение о том, что бот не работает с фото.\
\
![](Aspose.Words.4c056f22-99d5-45e7-95db-6115672f64c1.006.png)\
\
`           `**Вывод**

В ходе лабораторной работы был создан Telegram-бот с использованием библиотеки Aiogram и интеграцией с API OpenAI. Бот поддерживает системный промпт для задания контекста общения, обращается к пользователю по имени и <a name="_hlk217730442"></a>запоминает историю диалогов с помощью базы данных. Реализована команда /reset\_context для сброса истории, а также обработка различных типов медиа. В результате работы были получены навыки работы с асинхронным программированием, Telegram API и хранением данных, а также реализована поддержка контекста и взаимодействие с пользователем на более персонализированном уровне.

