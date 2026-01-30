import logging
import json
import random

from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "8136156824:AAFNQLJRVg4vLmYwLF1bVzNVS_Ie0lnkhBI"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Загружаем вопросы
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

# Состояние пользователя
users = {}


def get_new_question(user_id):
    if user_id not in users:
        users[user_id] = {
            "questions": random.sample(QUESTIONS, len(QUESTIONS)),
            "index": 0
        }

    data = users[user_id]

    if data["index"] >= len(data["questions"]):
        return None

    q = data["questions"][data["index"]]
    data["index"] += 1
    return q


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    users.pop(message.from_user.id, None)
    await message.answer(
        "Привет! 👋\n"
        "Я бот для подготовки к ОГЭ по английскому.\n\n"
        "Напиши /practice чтобы начать тренировку."
    )


@dp.message_handler(commands=["practice"])
async def practice(message: types.Message):
    user_id = message.from_user.id
    question = get_new_question(user_id)

    if question is None:
        await message.answer("Вопросы закончились 🎉\nНапиши /practice, чтобы начать заново.")
        return

    text = (
        f"📘 {question['type']}\n\n"
        f"{question['question']}\n\n"
        f"1) {question['options'][0]}\n"
        f"2) {question['options'][1]}\n"
        f"3) {question['options'][2]}\n"
        f"4) {question['options'][3]}\n\n"
        f"Напиши цифру ответа (1–4)"
    )

    users[user_id]["current"] = question
    await message.answer(text)


@dp.message_handler(lambda message: message.text in ["1", "2", "3", "4"])
async def answer(message: types.Message):
    user_id = message.from_user.id

    if user_id not in users or "current" not in users[user_id]:
        await message.answer("Напиши /practice чтобы начать.")
        return

    question = users[user_id]["current"]
    choice = int(message.text) - 1
    user_answer = question["options"][choice]

    if user_answer == question["correct"]:
        await message.answer("✅ Верно!")
    else:
        await message.answer(
            f"❌ Неверно.\nПравильный ответ: {question['correct']}"
        )

    # следующий вопрос
    next_question = get_new_question(user_id)

    if next_question is None:
        await message.answer("Тренировка окончена 🎓\nНапиши /practice, чтобы начать заново.")
        users.pop(user_id, None)
        return

    text = (
        f"📘 {next_question['type']}\n\n"
        f"{next_question['question']}\n\n"
        f"1) {next_question['options'][0]}\n"
        f"2) {next_question['options'][1]}\n"
        f"3) {next_question['options'][2]}\n"
        f"4) {next_question['options'][3]}\n\n"
        f"Напиши цифру ответа (1–4)"
    )

    users[user_id]["current"] = next_question
    await message.answer(text)


if name == "__main__":
    executor.start_polling(dp, skip_updates=True)
