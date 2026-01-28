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
    # логика выбора задания
    pass


@dp.callback_query_handler(lambda c: c.data.startswith("answer_"))
async def process_answer(callback_query: types.CallbackQuery):
    # обработка ответа
    pass


if name == "__main__":
    executor.start_polling(dp, skip_updates=True)
