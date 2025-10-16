# main.py
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.types import (
    Message,
    WebAppInfo,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    MenuButtonWebApp,
)

# -------------------------
# Config: try config.py then env
# -------------------------
try:
    from config import BOT_TOKEN, MINI_APP_URL
except Exception:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    MINI_APP_URL = os.getenv("MINI_APP_URL", "https://yourdomain.com/web/")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing — set it in config.py or env variable BOT_TOKEN")

# -------------------------
# Logging
# -------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# -------------------------
# Init bot
# -------------------------
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()
router = Router()

# -------------------------
# Menu button (WebApp)
# -------------------------
async def set_webapp_menu(bot: Bot):
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Мастерская", web_app=WebAppInfo(url=MINI_APP_URL))
        )
        logging.info("WebApp menu set.")
    except Exception as e:
        logging.warning(f"Couldn't set webapp menu: {e}")


# -------------------------
# Keyboards
# -------------------------
def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Начать путь", web_app=WebAppInfo(url=MINI_APP_URL))],
        [InlineKeyboardButton(text="🔍 Что я умею", callback_data="about_features")],
        [InlineKeyboardButton(text="📖 О книге", callback_data="about_book")],
        [InlineKeyboardButton(text="🛠 Поддержка", callback_data="support")],
    ])


def get_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ В начало", callback_data="back_to_start")]
    ])


# -------------------------
# /start handler
# -------------------------
@router.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        "👋 Привет.\n\n"
        "Ты не один. И ты не сломался.\n"
        "Это просто переход — и он имеет смысл.\n\n"
        "Я — твой цифровой проводник по книге «Найти себя».\n"
        "Всё здесь бесплатно. Просто будь с собой честен."
    )
    await message.answer(welcome_text, reply_markup=get_start_keyboard())


# -------------------------
# Callback handler
# -------------------------
@router.callback_query()
async def handle_callbacks(callback: types.CallbackQuery):
    data = callback.data or ""
    if data == "about_features":
        text = (
            "Я здесь, чтобы поддержать тебя:\n\n"
            "• 📍 Диагностика «6 уровней» — быстрое самощупие\n"
            "• 🔥 Тест на выгорание (Maslach) — оценка трёх шкал\n"
            "• 🌿 Практики: «Поле любви», «Преображение», «Соглашение с собой»\n"
            "• 📝 Дневник и шаблоны\n"
            "• 📬 Мягкие напоминания (опционально)"
        )
        await callback.message.edit_text(text, reply_markup=get_back_keyboard())

    elif data == "about_book":
        text = (
            "📖 «Найти себя» — практическая карта восстановления: "
            "от понимания симптомов к деликатным и работающим практикам.\n\n"
            "Если хотите — можно перейти в мини-приложение."
        )
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Купить (Ozon)", url="https://ozon.ru/t/HU6kW2c")],
            [InlineKeyboardButton(text="🚀 Перейти в Мастерскую", web_app=WebAppInfo(url=MINI_APP_URL))],
            [InlineKeyboardButton(text="◀️ В начало", callback_data="back_to_start")]
        ]))

    elif data == "support":
        text = (
            "Нужна помощь?\n\n"
            "• Техническая: сообщить проблему\n"
            "• Консультация: автор — Артём Графов\n"
            "• Тренинги: канал в Telegram"
        )
        await callback.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Сообщить о проблеме", callback_data="report_bug")],
            [InlineKeyboardButton(text="👤 Консультация", url="https://t.me/bartXIII")],
            [InlineKeyboardButton(text="🎓 Тренинги", url="https://t.me/naivedream")],
            [InlineKeyboardButton(text="◀️ В начало", callback_data="back_to_start")]
        ]))

    elif data == "report_bug":
        await callback.message.edit_text("Опиши, пожалуйста, проблему в следующем сообщении. Мы постараемся помочь.", reply_markup=get_back_keyboard())

    elif data == "back_to_start":
        await cmd_start(callback.message)

    await callback.answer()


# -------------------------
# WebApp data handler
# -------------------------
@router.message()
async def handle_webapp_data(message: Message):
    """
    Handles messages and web_app_data from the Mini App.
    The Mini App should send JSON strings via Telegram.WebApp.sendData({ ... }).
    """
    # handle data from WebApp
    webapp = getattr(message, "web_app_data", None)
    if webapp and getattr(webapp, "data", None):
        raw = webapp.data
        logging.info(f"Received web_app_data from {message.from_user.id}: {raw}")
        # raw is a stringified JSON from WebApp (client side)
        # We'll do simple substring checks and also try to parse JSON
        try:
            import json
            payload = json.loads(raw)
        except Exception:
            payload = {"_raw": raw}

        # Examples of actions we expect:
        # { action: "practice_completed", practice: "love-field" }
        # { action: "transformation_step", step: 2, note: "..." }
        # { action: "journal_save", text: "..." }
        # { action: "agreement_created", ... }

        action = payload.get("action") if isinstance(payload, dict) else None

        if action == "practice_completed":
            practice = payload.get("practice", "unknown")
            await message.answer(f"🌿 Спасибо — практика «{practice}» помечена как завершённая. Ты молодец.")
        elif action == "journal_save":
            await message.answer("📝 Запись дневника принята. Спасибо за честность.")
        elif action == "transformation_step":
            await message.answer("🔁 Шаг практики сохранен. Продолжай в своём темпе.")
        elif action == "agreement_created":
            await message.answer("📜 Соглашение с собой сохранено. Удачи на пути.")
        else:
            await message.answer("✅ Данные получены. Спасибо!")

    else:
        # Plain text message—interpret as support message if user says so
        text = (message.text or "").lower()
        if "помощ" in text or "проблем" in text or "support" in text:
            # In a real app, forward to support chat or save to DB
            await message.answer("Спасибо, мы получили вашу просьбу о поддержке. Оператор ответит в ближайшее время.")
        else:
            # Default reply with quick button to WebApp
            await message.answer(
                "Чтобы вернуться в Мастерскую, нажмите кнопку:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏡 В Мастерскую", web_app=WebAppInfo(url=MINI_APP_URL))]
                ])
            )


# -------------------------
# Start
# -------------------------
dp.include_router(router)


async def main():
    await set_webapp_menu(bot)
    logging.info("Bot polling started.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
