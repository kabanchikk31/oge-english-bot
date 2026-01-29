import logging
import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8136156824:AAFNQLJRVg4vLmYwLF1bVzNVS_Ie0lnkhBI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


# ======================
# Работа с базой
# ======================
def get_question():
    try:
        conn = sqlite3.connect("questions.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM questions")
        count = cursor.fetchone()[0]

        if count == 0:
            conn.close()
            return None

        cursor.execute("""
            SELECT id, question, option_a, option_b, option_c, option_d, correct
            FROM questions
            ORDER BY RANDOM()
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()
        return row

    except Exception as e:
        return f"ERROR:{e}"


# ======================
# Команда /start
# ======================
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📝 Практика", callback_data="practice"))

    await message.answer(
        "👋 Привет!\n"
        "Я бот для подготовки к ОГЭ по английскому 🇬🇧\n\n"
        "Нажми «Практика», чтобы начать.",
        reply_markup=kb
    )


# ======================
# Кнопка «Практика»
# ======================
@dp.callback_query_handler(lambda c: c.data == "practice")
async def practice(callback_query: types.CallbackQuery):
    await callback_query.answer()  # ОБЯЗАТЕЛЬНО

    q = get_question()

    if q is None:
        await callback_query.message.answer(
            "❗ В базе пока нет заданий."
        )
        return

    if isinstance(q, str) and q.startswith("ERROR"):
        await callback_query.message.answer(
            f"❌ Ошибка базы данных:\n{q}"
        )
        return

    q_id, text, a, b, c, d, correct = q

    message_text = (
        "📘 Задание ОГЭ (тест)\n\n"
        f"{text}"
    )

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(a, callback_data=f"answer_{q_id}_A"),
        InlineKeyboardButton(b, callback_data=f"answer_{q_id}_B"),
        InlineKeyboardButton(c, callback_data=f"answer_{q_id}_C"),
        InlineKeyboardButton(d, callback_data=f"answer_{q_id}_D"),
    )

    await callback_query.message.answer(message_text, reply_markup=kb)


# ======================
# Обработка ответа
# ======================
@dp.callback_query_handler(lambda c: c.data.startswith("answer_"))
async def process_answer(callback_query: types.CallbackQuery):
    await callback_query.answer()

    _, q_id, user_answer = callback_query.data.split("_")

    conn = sqlite3.connect("questions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT correct FROM questions WHERE id = ?", (q_id,))
    correct = cursor.fetchone()[0]
    conn.close()

    if user_answer == correct:
        text = "✅ Верно!"
    else:
        text = f"❌ Неверно.\nПравильный ответ: {correct}"

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📝 Следующий вопрос", callback_data="practice"))

    await callback_query.message.answer(text, reply_markup=kb)


# ======================
# Запуск бота
# ======================
if name == "__main__":
    executor.start_polling(dp, skip_updates=True)
