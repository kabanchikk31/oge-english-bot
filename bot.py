import logging
import sqlite3

from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = "8136156824:AAFNQLJRVg4vLmYwLF1bVzNVS_Ie0lnkhBI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📝 Практика", callback_data="practice"))
    await message.answer("Выбери режим:", reply_markup=kb)


@dp.callback_query_handler(lambda c: c.data == "practice")
async def practice(callback_query: types.CallbackQuery):
    q = get_question()

    if not q:
        await callback_query.message.answer(
            "❗ В базе пока нет заданий.\n"
            "Добавь вопросы в базу данных."
        )
        await callback_query.answer()
        return

    q_id, text, a, b, c, d, correct = q

    message_text = (
        "📘 Задание ОГЭ\n\n"
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
    await callback_query.answer()


@dp.callback_query_handler(lambda c: c.data.startswith("answer_"))
async def process_answer(callback_query: types.CallbackQuery):
    # обработка ответа
    pass


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
