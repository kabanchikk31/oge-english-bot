import logging
import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8136156824:AAFNQLJRVg4vLmYwLF1bVzNVS_Ie0lnkhBI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Храним состояние пользователей
user_state = {}

# ---------- БАЗА ----------
def get_question():
    conn = sqlite3.connect("questions.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, question, option_a, option_b, option_c, option_d, correct
        FROM questions
        ORDER BY RANDOM()
        LIMIT 1
    """)

    q = cursor.fetchone()
    conn.close()
    return q

# ---------- КЛАВИАТУРЫ ----------
def main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📝 Практика", callback_data="practice"))
    return kb

def exit_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="menu"))
    return kb

# ---------- /start ----------
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    user_state.pop(message.from_user.id, None)
    await message.answer(
        "👋 Привет! Я бот для подготовки к ОГЭ по английскому 🇬🇧",
        reply_markup=main_menu()
    )

# ---------- Главное меню ----------
@dp.callback_query_handler(lambda c: c.data == "menu")
async def menu(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_state.pop(callback_query.from_user.id, None)
    await callback_query.message.answer(
        "Главное меню:",
        reply_markup=main_menu()
    )

# ---------- Практика ----------
@dp.callback_query_handler(lambda c: c.data == "practice")
async def practice(callback_query: types.CallbackQuery):
    await callback_query.answer()

    user_id = callback_query.from_user.id

    # Если вопрос уже активен — не даём новый
    if user_id in user_state:
        await callback_query.message.answer(
            "❗ Сначала ответь на текущий вопрос",
            reply_markup=exit_menu()
        )
        return

    q = get_question()
    if not q:
        await callback_query.message.answer("❌ В базе нет заданий")
        return

    q_id, text, a, b, c, d, correct = q

    user_state[user_id] = {
        "question_id": q_id,
        "correct": correct
    }

    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton(a, callback_data=f"ans_A"),
        InlineKeyboardButton(b, callback_data=f"ans_B"),
        InlineKeyboardButton(c, callback_data=f"ans_C"),
        InlineKeyboardButton(d, callback_data=f"ans_D"),
    )
    kb.add(InlineKeyboardButton("🏠 В главное меню", callback_data="menu"))

    await callback_query.message.answer(
        f"📘 Задание ОГЭ:\n\n{text}",
        reply_markup=kb
    )

# ---------- Ответ ----------
@dp.callback_query_handler(lambda c: c.data.startswith("ans_"))
async def answer(callback_query: types.CallbackQuery):
    await callback_query.answer()

    user_id = callback_query.from_user.id

    if user_id not in user_state:
        await callback_query.message.answer(
            "❗ Этот вопрос уже неактивен",
            reply_markup=main_menu()
        )
        return

    chosen = callback_query.data.split("_")[1]

    conn = sqlite3.connect("questions.db")
    cursor = conn.cursor()

    q_id = user_state[user_id]["question_id"]
    correct_letter = user_state[user_id]["correct"]

    cursor.execute(f"""
        SELECT option_{correct_letter.lower()}
        FROM questions
        WHERE id = ?
    """, (q_id,))
    correct_text = cursor.fetchone()[0]

    conn.close()
    user_state.pop(user_id)

    if chosen == correct_letter:
        await callback_query.message.answer(
            "✅ Верно!",
            reply_markup=main_menu()
        )
    else:
        await callback_query.message.answer(
            f"❌ Неверно.\nПравильный ответ:\n👉 {correct_text}",
            reply_markup=main_menu()
        )

# ---------- Запуск ----------
if name == "__main__":
    executor.start_polling(dp, skip_updates=True)
