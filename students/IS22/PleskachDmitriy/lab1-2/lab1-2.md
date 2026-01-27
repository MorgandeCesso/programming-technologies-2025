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

Цель лабораторной работы - получение навыков работы с библиотекой Aiogram, связка API OpenAI и написанного бота.

Инструменты и настройки:

- Язык программирования: Python.
- Библиотеки:

  openai - для работы с API.

  dotenv - для загрузки переменных окружения (например, API-ключ).

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
Добавление функции обращения к пользователю по имени: Для того чтобы бот знал имя пользователя, используем атрибут message.from_user.full_name

```python
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}! Я бот-ассистент."
    )

async def get_response(
    message: str, username: str, context_data: str, client: AsyncOpenAI
) -> str:
    personalized_prompt = (
        SYSTEM_PROMPT.format(username=username)
        if "{username}" in SYSTEM_PROMPT
        else f"{SYSTEM_PROMPT} Общайся с пользователем по имени {username}."
    )

    response = await client.responses.create(
        model="gpt-4.1-nano",
        input=full_message,
        instructions=personalized_prompt,
        temperature=TEMPERATURE,
    )
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
```
Для того, чтобы ИИ помнил контекст общения с пользователем, была реализована система ведения истории диалога. У каждого пользователя свой сохраненный контекст.

Для упрощения задачи и быстрого прототипирования я решил использовать файл SQLite для хранения истории сообщений и подключаться к нему, что позволяет эффективно управлять данными без необходимости использования более сложных баз данных. Это обеспечило простоту реализации и ускорение процесса разработки, что идеально подходит для учебного прототипа.

Для управления состоянием диалога реализована команда /reset_context, предназначенная для сброса текущего контекста общения.

```python
def clear_history(self, user_id: int) -> int:
    updated_count = (
        self.session.query(Message)
        .filter(Message.user_id == user_id, Message.in_history == True)
        .update({"in_history": False})
    )
    self.session.commit()
    return updated_count
```

```python
@dp.message(Command("reset_context"))
async def command_reset_context_handler(message: Message) -> None:
    user_id = message.from_user.id
    db_manager.clear_history(user_id)
    await message.answer("Контекст диалога успешно сброшен.")
```
Для реализации команды /reset_context, предназначенной для сброса контекста диалога, используется единая сессия базы данных, инициализируемая при запуске приложения. При получении команды определяется пользователь по его уникальному user_id, извлекаемому из объекта сообщения. Далее выполняется логическое обновление истории сообщений данного пользователя: все записи, участвующие в формировании текущего контекста диалога, помечаются как неактуальные путём изменения значения флага in_history. Изменения фиксируются в базе данных без пересоздания соединения или повторной инициализации сессии. В результате текущий контекст диалога считается сброшенным, а последующие сообщения пользователя формируют новый контекст общения. После выполнения операции пользователю отправляется сообщение, подтверждающее успешный сброс контекста.

![](assets/2.png)
\
![](assets/3.png)

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
![](assets/6.png)\
\
`           `**Вывод**

В ходе лабораторной работы был создан Telegram-бот с использованием библиотеки Aiogram и интеграцией с API OpenAI. Бот поддерживает системный промпт для задания контекста общения, обращается к пользователю по имени и <a name="_hlk217730442"></a>запоминает историю диалогов с помощью базы данных. Реализована команда /reset_context для сброса истории, а также обработка различных типов медиа. В результате работы были получены навыки работы с асинхронным программированием, Telegram API и хранением данных, а также реализована поддержка контекста и взаимодействие с пользователем на более персонализированном уровне.

