import asyncio
import logging
from aiogram import Bot, Dispatcher, Router, types
from aiogram.types import (
    Message,
    WebAppInfo,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp
)
from aiogram.filters import Command
from config import BOT_TOKEN, MINI_APP_URL
# main.py — в самом начале, до создания бота
import os

print("🔍 Все переменные окружения (частично):")
for key in os.environ.keys():
    if "BOT" in key or "TOKEN" in key or "APP" in key:
        print(f"  {key} = {os.environ[key][:20]}...")  # первые 20 символов

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(f"🎯 BOT_TOKEN = {repr(BOT_TOKEN)}")  # покажет None, если нет

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Главное меню с WebApp (опционально)


async def set_webapp_menu(bot: Bot):
    await bot.set_chat_menu_button(
        menu_button=MenuButtonWebApp(
            text="Мастерская", web_app=WebAppInfo(url=MINI_APP_URL))
    )

# Клавиатура для приветствия


def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать путь",
                              web_app=WebAppInfo(url=MINI_APP_URL))],
        [InlineKeyboardButton(text="🔍 Что я умею",
                              callback_data="about_features")],
        [InlineKeyboardButton(text="📖 О книге", callback_data="about_book")],
        [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")]
    ])

# Клавиатура "в начало"


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ В начало",
                              callback_data="back_to_start")]
    ])


@router.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "👋 Привет.\n"
        "Ты не один. И ты не сломался.\n"
        "Это просто переход — и он имеет смысл.\n"
        "Я — твой цифровой проводник по книге \"Найти себя\".\n"
        "Всё здесь бесплатно. Просто будь с собой честен."
    )
    await message.answer(welcome_text, reply_markup=get_start_keyboard())

# Обработка callback-кнопок


@router.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    if callback.data == "about_features":
        text = (
            "Я здесь, чтобы быть твоей опорой на этом пути. Вот что мы можем делать вместе:\n\n"
            "📍 Понять, где ты сейчас: Проведем честную диагностику твоего состояния без сложных терминов.\n"
            "🧭 Найти ориентиры: Покажу, на каком из 6 уровней книги у тебя больше всего напряжения, а где — твоя сила.\n"
            "🛠️ Дать инструменты: Проведу тебя по ключевым практикам из книги — «Поле любви», «Преображение» и другим.\n"
            "📝 Поддержать в самопознании: Помогу вести дневник и буду задавать вопросы, которые ведут вглубь.\n"
            "📬 Мягко напомнить о себе: Если ты пропадешь, я тихонько постучусь, чтобы спросить, как ты."
        )
        await callback.message.edit_text(text, reply_markup=get_back_keyboard())

    elif callback.data == "about_book":
        text = (
            "Книга \"Найти себя\" — это не сборник советов, а живая карта внутреннего путешествия от выгорания к целостности.\n\n"
            "Она для тех, кто оказался в точке жизненного кризиса: когда привычные цели больше не вдохновляют, работа не приносит радости, а на вопрос \"Чего я хочу?\" ответа нет.\n\n"
            "Если у тебя ее еще нет, она может стать твоим настольным компасом."
        )
        # Добавь обложку, если есть
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Купить на Ozon",
                                  url="https://www.ozon.ru/...")],
            [InlineKeyboardButton(text="🚀 Поехали далее",
                                  web_app=WebAppInfo(url=MINI_APP_URL))],
            [InlineKeyboardButton(text="◀️ В начало",
                                  callback_data="back_to_start")]
        ]))

    elif callback.data == "support":
        text = (
            "Иногда в пути нужна помощь.\n\n"
            "Техническая проблема с ботом? Нажми кнопку ниже, и твой вопрос улетит нашей команде.\n\n"
            "Чувствуешь, что нужна личная работа и глубокое погружение? Автор книги, Артём Графов, проводит личные консультации.\n\n"
            "Если интересно узнать о групповых тренингах - смотри информацию по кнопке"
        )
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🤖 Сообщить о проблеме", callback_data="report_bug")],
            [InlineKeyboardButton(
                text="👤 Консультация с автором", url="https://t.me/artyom_grafov")],
            [InlineKeyboardButton(
                text="🎓 Тренинги", url="https://t.me/kanal_masterskaya")],
            [InlineKeyboardButton(text="◀️ В начало",
                                  callback_data="back_to_start")]
        ]))

    elif callback.data == "report_bug":
        await callback.message.edit_text(
            "Пожалуйста, опиши проблему в следующем сообщении. Мы обязательно поможем!",
            reply_markup=get_back_keyboard()
        )
        # Включаем режим ожидания сообщения для поддержки
        # (в реальном проекте — сохранить состояние через FSM)

    elif callback.data == "back_to_start":
        await cmd_start(callback.message)

    await callback.answer()

# Обработка данных из Mini App


@router.message()
async def handle_webapp_data(message: Message):
    if message.web_app_data:
        data = message.web_app_data.data
        user = message.from_user
        # Логируем или обрабатываем событие
        print(f"Mini App data from {user.id}: {data}")

        # Пример: если пользователь завершил практику
        if '"action":"practice_completed"' in data:
            await message.answer(
                "🌿 Спасибо, что прошёл(ла) практику! Ты делаешь важный шаг к себе.\n\n"
                "Если захочешь продолжить — просто нажми на кнопку ниже.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="🔄 Вернуться в Мастерскую", web_app=WebAppInfo(url=MINI_APP_URL))]
                ])
            )
        else:
            await message.answer("Данные получены. Спасибо!")
    else:
        # Обычное текстовое сообщение (например, в поддержку)
        # Здесь можно пересылать в чат поддержки
        if "сообщить о проблеме" in str(message.text).lower():
            pass  # можно реализовать FSM
        else:
            await message.answer("Я понял. Чтобы вернуться в Мастерскую, нажми кнопку ниже:",
                                 reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                     [InlineKeyboardButton(
                                         text="🏡 В Мастерскую", web_app=WebAppInfo(url=MINI_APP_URL))]
                                 ]))

# Регистрация роутеров
dp.include_router(router)

# Запуск


async def main():
    await set_webapp_menu(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
