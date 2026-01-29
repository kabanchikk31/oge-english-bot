import logging
import random
import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8136156824:AAFNQLJRVg4vLmYwLF1bVzNVS_Ie0lnkhBI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_sessions = {}


def get_questions():
    conn = sqlite3.connect("questions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT question, option_a, option_b, option_c, option_d, correct FROM questions")
    rows = cursor.fetchall()
    conn.close()
    return rows


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📝 Практика", callback_data="practice"),
        InlineKeyboardButton("📘 Теория", callback_data="theory")
    )
    await message.answer("Привет! Я бот для подготовки к ОГЭ по английскому 🇬🇧\nВыбери режим:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data == "theory")
async def theory(callback_query: types.CallbackQuery):
    await callback_query.message.answer(
        "📘 Теория\n\n"
        "В этом разделе будут:\n"
        "• времена английского языка\n"
        "• основные грамматические правила\n"
        "• лексика ОГЭ\n\n"
        "Раздел в разработке 👷‍♂️"
    )


@dp.callback_query_handler(lambda c: c.data == "practice")
async def practice(callback_query: types.CallbackQuery):
    questions = get_questions()
    random.shuffle(questions)

    user_sessions[callback_query.from_user.id] = {
        "questions": questions,
        "current": 0,
        "score": 0
    }

    await send_question(callback_query.message, callback_query.from_user.id)


async def send_question(message, user_id):
    session = user_sessions[user_id]
    q = session["questions"][session["current"]]

    question_text, a, b, c, d, correct = q

    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(a, callback_data=f"answer|{a}"),
        InlineKeyboardButton(b, callback_data=f"answer|{b}"),
        InlineKeyboardButton(c, callback_data=f"answer|{c}"),
        InlineKeyboardButton(d, callback_data=f"answer|{d}")
    )

    await message.answer(
        f"Вопрос {session['current'] + 1}/{len(session['questions'])}\n\n{question_text}",
        reply_markup=kb
    )


@dp.callback_query_handler(lambda c: c.data.startswith("answer|"))
async def process_answer(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    session = user_sessions[user_id]

    chosen = callback_query.data.split("|")[1]
    correct = session["questions"][session["current"]][5]

    if chosen == correct:
        session["score"] += 1
        await callback_query.message.answer("✅ Верно!")
    else:
        await callback_query.message.answer(
            f"❌ Неверно.\nПравильный ответ: **{correct}**",
            parse_mode="Markdown"
        )

    session["current"] += 1

    if session["current"] < len(session["questions"]):
        await send_question(callback_query.message, user_id)
    else:
        await callback_query.message.answer(
            f"🏁 Практика окончена!\n"
            f"Твой результат: {session['score']} из {len(session['questions'])}"
        )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
