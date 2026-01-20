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

from config import OPENAI\_API\_KEY, SYSTEM\_PROMPT, TEMPERATURE

async def get\_response(

`    `message: str, username: str, context\_data: str, client: AsyncOpenAI

) -> str:

`    `try:

`        `personalized\_prompt = (

`            `SYSTEM\_PROMPT.format(username=username)

`            `if "{username}" in SYSTEM\_PROMPT

`            `else f"{SYSTEM\_PROMPT} Общайся с пользователем по имени {username}."

`        `)


`        `response = await client.responses.create(

`            `model="gpt-4.1-nano",

`            `input=message,

`            `instructions=personalized\_prompt,

`            `temperature=TEMPERATURE,

`        `)

`        `return response.output\_text

Переменная SYSTEM\_PROMPT= «Ты маэстро музыки, разбираешься во всех тонкостях музыки и чинишь гитары. Веди себя надменно как будто ты все знаешь и для тебя все очевидно.»

Результат работы:

Бот генерирует ответы, используя системный контекст.

\
![](assets/1.png)

\
Добавление функции обращения к пользователю по имени: Для того чтобы бот знал имя пользователя, используем атрибут message.from\_user.full\_name

@dp.message(CommandStart())

async def start(message: Message):

`    `await message.answer(

`        `f"Привет, {message.from\_user.full\_name}! Я бот-ассистент."

`    `)

@dp.message(Command("reset\_context"))

async def reset\_context(message: Message):

`    `db.clear(message.from\_user.id)

`    `await message.answer("Контекст диалога сброшен.")и передаем в функцию запроса к ChatGPT через системный промт

async def get\_response(

`    `message: str, username: str, context\_data: str, client: AsyncOpenAI

) -> str:

`    `try:

`        `personalized\_prompt = (

`            `SYSTEM\_PROMPT.format(username=username)

`            `if "{username}" in SYSTEM\_PROMPT

`            `else f"{SYSTEM\_PROMPT} Общайся с пользователем по имени {username}."

`        `)


`        `response = await client.responses.create(

`            `model="gpt-4.1-nano",

`            `input=full\_message,

`            `instructions=personalized\_prompt,

`            `temperature=TEMPERATURE,

`        `)

`        `return response.output\_text

Добавление хранения истории сообщений и поддержку контекста диалога:

class Message(Base):

`    `\_\_tablename\_\_ = "messages"

`    `id = Column(Integer, primary\_key=True, index=True)

`    `user\_id = Column(Integer, index=True)

`    `username = Column(String)

`    `user\_message = Column(Text)

`    `assistant\_message = Column(Text)

`    `created\_at = Column(DateTime, default=func.now())

`    `in\_history = Column(Boolean, default=True)

class DatabaseManager:

`    `def get\_last\_messages(self, user\_id: int, limit: int = 5) -> list[dict]:

`        `session = self.SessionLocal()

`        `try:

`            `msgs = (

`                `session.query(Message)

.filter(Message.user\_id == user\_id, Message.in\_history == True)

.order\_by(Message.created\_at.desc())

.limit(limit)

.all()

`            `)

`            `msgs = list(reversed(msgs))

`            `result = []

`            `for msg in msgs:

`                `result.append(

`                    `{

`                        `"user\_message": msg.user\_message,

`                        `"assistant\_message": msg.assistant\_message,

`                    `}

`                `)

`            `return result

`        `finally:

`            `session.close()

Для того, чтобы ИИ помнил контекст общения с пользователем, была реализована система ведения истории диалога. История ограницивается 10 последними сообщениями. У каждого пользователя свой сохраненный контекст.

Для упрощения задачи и быстрого прототипирования я решил использовать файл SQLite для хранения истории сообщений и подключаться к нему, что позволяет эффективно управлять данными без необходимости использования более сложных баз данных. Это обеспечило простоту реализации и ускорение процесса разработки, что идеально подходит для учебного прототипа.

Добавление команды /resetcontext, которая будет сбрасывать контекст диалога

@dp.message(Command("reset\_context"))

async def command\_reset\_context\_handler(message: Message) -> None:

`    `try:

`        `user\_id = message.from\_user.id

`        `db\_manager.clear\_history(user\_id)

`        `file\_path = f"data\_json/history\_{user\_id}.json"

`        `if os.path.exists(file\_path):

`            `with open(file\_path, "w", encoding="utf-8") as f:

`                `json.dump([], f, ensure\_ascii=False, indent=2)

`        `await message.answer("Контекст диалога успешно сброшен.")

`    `except Exception as e:

`        `logging.error(f"Error occurred: {e}")

`        `await message.answer("Произошла ошибка при сбросе контекста диалога.")

def clear\_history(self, user\_id: int) -> int:

`    `session = self.SessionLocal()

`    `try:

`        `updated\_count = (

`            `session.query(Message)

.filter(Message.user\_id == user\_id, Message.in\_history == True)

.update({"in\_history": False})

`        `)

`        `session.commit()

`        `return updated\_count

`    `finally:

`        `session.close()

Для реализации команды /reset\_context, которая сбрасывает контекст диалога, я создал обработчик для этой команды, который проверяет, есть ли сохраненная история для конкретного пользователя, используя его уникальный user\_id. Когда пользователь отправляет команду /resetcontext, я извлекаю его user\_id из сообщения с помощью message.from\_user.id. Затем, проверяя, существует ли история диалога этого user\_id в таблице, я меняю флаг у сообщений, чтобы они больше не использовались в истории и также отчищаю JSON, который хранит историю в рамках одной сессии. После этого отправляется сообщение, подтверждающее, что история была сброшена и можно начать новый разговор.

![](assets/2.png)
\
![](assets/3.png)\
\
Добавление хранения истории сообщений и поддержку контекста диалога:

class Message(Base):

`    `\_\_tablename\_\_ = "messages"

`    `id = Column(Integer, primary\_key=True, index=True)

`    `user\_id = Column(Integer, index=True)

`    `username = Column(String)

`    `user\_message = Column(Text)

`    `assistant\_message = Column(Text)

`    `created\_at = Column(DateTime, default=func.now())

`    `in\_history = Column(Boolean, default=True)

class DatabaseManager:

`    `def get\_last\_messages(self, user\_id: int, limit: int = 5) -> list[dict]:

`        `session = self.SessionLocal()

`        `try:

`            `msgs = (

`                `session.query(Message)

.filter(Message.user\_id == user\_id, Message.in\_history == True)

.order\_by(Message.created\_at.desc())

.limit(limit)

.all()

`            `)

`            `msgs = list(reversed(msgs))

`            `result = []

`            `for msg in msgs:

`                `result.append(

`                    `{

`                        `"user\_message": msg.user\_message,

`                        `"assistant\_message": msg.assistant\_message,

`                    `}

`                `)

`            `return result

`        `finally:

`            `session.close()

Для того, чтобы ИИ помнил контекст общения с пользователем, была реализована система ведения истории диалога. История ограницивается 10 последними сообщениями. У каждого пользователя свой сохраненный контекст.

Для упрощения задачи и быстрого прототипирования я решил использовать файл SQLite для хранения истории сообщений и подключаться к нему, что позволяет эффективно управлять данными без необходимости использования более сложных баз данных. Это обеспечило простоту реализации и ускорение процесса разработки, что идеально подходит для учебного прототипа.

Добавление команды /reset\_context, которая будет сбрасывать контекст диалога

@dp.message(Command("reset\_context"))

async def command\_reset\_context\_handler(message: Message) -> None:

`    `try:

`        `user\_id = message.from\_user.id

`        `db\_manager.clear\_history(user\_id)

`        `file\_path = f"data\_json/history\_{user\_id}.json"

`        `if os.path.exists(file\_path):

`            `with open(file\_path, "w", encoding="utf-8") as f:

`                `json.dump([], f, ensure\_ascii=False, indent=2)

`        `await message.answer("Контекст диалога успешно сброшен.")

`    `except Exception as e:

`        `logging.error(f"Error occurred: {e}")

`        `await message.answer("Произошла ошибка при сбросе контекста диалога.")

def clear\_history(self, user\_id: int) -> int:

`    `session = self.SessionLocal()

`    `try:

`        `updated\_count = (

`            `session.query(Message)

.filter(Message.user\_id == user\_id, Message.in\_history == True)

.update({"in\_history": False})

`        `)

`        `session.commit()

`        `return updated\_count

`    `finally:

`        `session.close()

Для реализации команды /reset\_context, которая сбрасывает контекст диалога, я создал обработчик для этой команды, который проверяет, есть ли сохраненная история для конкретного пользователя, используя его уникальный user\_id. Когда пользователь отправляет команду /resetcontext, я извлекаю его user\_id из сообщения с помощью message.from\_user.id. Затем, проверяя, существует ли история диалога этого user\_id в таблице, я меняю флаг у сообщений, чтобы они больше не использовались в истории и также отчищаю JSON, который хранит историю в рамках одной сессии. После этого отправляется сообщение, подтверждающее, что история была сброшена и можно начать новый разговор.



![](assets/4.png)
![](assets/5.png)\
\
Добавление поддержки отправки изображений (без их обработки нейронкой).

@dp.message()

async def message\_handler(message: Message) -> None:

`    `try:

`        `if message.photo:

`            `await message.answer(

`                `"Вы отправили картинку! К сожалению, я не могу обрабатывать изображения."

`            `)

`            `Return

Для обработки сообщений, отличных от текста (например, изображений, видео и других медиа), я добавил проверку типа сообщения с помощью message.photo,которое проверяет, является ли отперавленое сообщение фотографией. Если да, то вывожу пользователю сообщение о том, что бот не работает с фото.\
\
![](Aspose.Words.4c056f22-99d5-45e7-95db-6115672f64c1.006.png)\
\
`           `**Вывод**

В ходе лабораторной работы был создан Telegram-бот с использованием библиотеки Aiogram и интеграцией с API OpenAI. Бот поддерживает системный промпт для задания контекста общения, обращается к пользователю по имени и <a name="_hlk217730442"></a>запоминает историю диалогов с помощью базы данных. Реализована команда /reset\_context для сброса истории, а также обработка различных типов медиа. В результате работы были получены навыки работы с асинхронным программированием, Telegram API и хранением данных, а также реализована поддержка контекста и взаимодействие с пользователем на более персонализированном уровне.

