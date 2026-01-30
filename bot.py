import logging
import json
import random

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8136156824:AAFNQLJRVg4vLmYwLF1bVzNVS_Ie0lnkhBI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# ─── Загрузка вопросов ───
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

user_states = {}  # хранит текущий вопрос для пользователя


# ─── Старт ───
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📝 Практика", callback_data="practice"))
    await message.answer("Привет! Выбери режим:", reply_markup=kb)


# ─── Практика ───
@dp.callback_query_handler(lambda c: c.data == "practice")
async def practice(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    question = random.choice(QUESTIONS)
    user_states[user_id] = question

    kb = InlineKeyboardMarkup(row_width=1)
    for option in question["options"]:
        kb.add(
            InlineKeyboardButton(
                option,
                callback_data=f"answer|{option}"
            )
        )

    kb.add(InlineKeyboardButton("⬅️ В меню", callback_data="menu"))

    text = (
        f"📘 Задание ОГЭ: {question['type']}\n\n"
        f"{question['question']}"
    )

    await callback_query.message.answer(text, reply_markup=kb)
    await callback_query.answer()


# ─── Ответ ───
@dp.callback_query_handler(lambda c: c.data.startswith("answer|"))
async def process_answer(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_states:
        await callback_query.answer("Начни заново через /start", show_alert=True)
        return

    user_answer = callback_query.data.split("|")[1]
    question = user_states[user_id]

    if user_answer == question["correct"]:
        await callback_query.message.answer("✅ Верно!")
    else:
        await callback_query.message.answer(
            f"❌ Неверно.\n"
            f"Правильный ответ: {question['correct']}"
        )

    await callback_query.answer()


# ─── Меню ───
@dp.callback_query_handler(lambda c: c.data == "menu")
async def back_to_menu(callback_query: types.CallbackQuery):
    await start(callback_query.message)
    await callback_query.answer()


# ─── Запуск ───
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
